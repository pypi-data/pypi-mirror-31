"""
Utility routines
"""
import re
import warnings
import collections
from copy import deepcopy
import sys
import traceback

import six
import pandas as pd
import numpy as np

try:
    from pandas.api.types import infer_dtype
except ImportError: # Pandas before 0.20.0
    from pandas.lib import infer_dtype

from .schemapi import SchemaBase, Undefined


TYPECODE_MAP = {'ordinal': 'O',
                'nominal': 'N',
                'quantitative': 'Q',
                'temporal': 'T'}

INV_TYPECODE_MAP = {v: k for k, v in TYPECODE_MAP.items()}


def infer_vegalite_type(data):
    """
    From an array-like input, infer the correct vega typecode
    ('ordinal', 'nominal', 'quantitative', or 'temporal')

    Parameters
    ----------
    data: Numpy array or Pandas Series
    """
    # Otherwise, infer based on the dtype of the input
    typ = infer_dtype(data)

    # TODO: Once this returns 'O', please update test_select_x and test_select_y in test_api.py

    if typ in ['floating', 'mixed-integer-float', 'integer',
               'mixed-integer', 'complex']:
        return 'quantitative'
    elif typ in ['string', 'bytes', 'categorical', 'boolean', 'mixed', 'unicode']:
        return 'nominal'
    elif typ in ['datetime', 'datetime64', 'timedelta',
                 'timedelta64', 'date', 'time', 'period']:
        return 'temporal'
    else:
        warnings.warn("I don't know how to infer vegalite type from '{0}'.  "
                      "Defaulting to nominal.".format(typ))
        return 'nominal'


def sanitize_dataframe(df):
    """Sanitize a DataFrame to prepare it for serialization.

    * Make a copy
    * Raise ValueError if it has a hierarchical index.
    * Convert categoricals to strings.
    * Convert np.bool_ dtypes to Python bool objects
    * Convert np.int dtypes to Python int objects
    * Convert floats to objects and replace NaNs by None.
    * Convert DateTime dtypes into appropriate string representations
    """
    df = df.copy()

    if isinstance(df.index, pd.core.index.MultiIndex):
        raise ValueError('Hierarchical indices not supported')
    if isinstance(df.columns, pd.core.index.MultiIndex):
        raise ValueError('Hierarchical indices not supported')

    def to_list_if_array(val):
        if isinstance(val, np.ndarray):
            return val.tolist()
        else:
            return val

    for col_name, dtype in df.dtypes.iteritems():
        if str(dtype) == 'category':
            # XXXX: work around bug in to_json for categorical types
            # https://github.com/pydata/pandas/issues/10778
            df[col_name] = df[col_name].astype(str)
        elif str(dtype) == 'bool':
            # convert numpy bools to objects; np.bool is not JSON serializable
            df[col_name] = df[col_name].astype(object)
        elif np.issubdtype(dtype, np.integer):
            # convert integers to objects; np.int is not JSON serializable
            df[col_name] = df[col_name].astype(object)
        elif np.issubdtype(dtype, np.floating):
            # For floats, convert nan->None: np.float is not JSON serializable
            col = df[col_name].astype(object)
            df[col_name] = col.where(col.notnull(), None)
        elif str(dtype).startswith('datetime'):
            # Convert datetimes to strings
            # astype(str) will choose the appropriate resolution
            df[col_name] = df[col_name].astype(str).replace('NaT', '')
        elif dtype == object:
            # Convert numpy arrays saved as objects to lists
            # Arrays are not JSON serializable
            col = df[col_name].apply(to_list_if_array, convert_dtype=False)
            df[col_name] = col.where(col.notnull(), None)
    return df


def _parse_shorthand(shorthand):
    """
    Parse the shorthand expression for aggregation, field, and type.

    These are of the form:

    - "col_name"
    - "col_name:O"
    - "average(col_name)"
    - "average(col_name):O"

    Parameters
    ----------
    shorthand: str
        Shorthand string

    Returns
    -------
    D : dict
        Dictionary containing the field, aggregate, and typecode
    """
    if not shorthand:
        return {}

    # List taken from vega-lite v2 AggregateOp
    valid_aggregates = ["argmax", "argmin", "average", "count", "distinct",
                        "max", "mean", "median", "min", "missing", "q1", "q3",
                        "ci0", "ci1", "stderr", "stdev", "stdevp", "sum",
                        "valid", "values", "variance", "variancep"]
    valid_typecodes = list(TYPECODE_MAP) + list(INV_TYPECODE_MAP)

    # build regular expressions
    units = dict(field='(?P<field>.*)',
                 type='(?P<type>{0})'.format('|'.join(valid_typecodes)),
                 count='(?P<aggregate>count)',
                 aggregate='(?P<aggregate>{0})'.format('|'.join(valid_aggregates)))
    patterns = [r'{count}\(\)',
                r'{count}\(\):{type}',
                r'{aggregate}\({field}\):{type}',
                r'{aggregate}\({field}\)',
                r'{field}:{type}',
                r'{field}']
    regexps = (re.compile('\A' + p.format(**units) + '\Z', re.DOTALL)
               for p in patterns)

    # find matches depending on valid fields passed
    match = next(exp.match(shorthand).groupdict() for exp in regexps
                 if exp.match(shorthand))

    # Handle short form of the type expression
    type_ = match.get('type', None)
    if type_:
        match['type'] = INV_TYPECODE_MAP.get(type_, type_)

    # counts are quantitative by default
    if match == {'aggregate': 'count'}:
        match['type'] = 'quantitative'

    return match


def parse_shorthand(shorthand, data=None):
    """Parse the shorthand expression for aggregation, field, and type.

    These are of the form:

    - "col_name"
    - "col_name:O"
    - "average(col_name)"
    - "average(col_name):O"

    Optionally, a dataframe may be supplied, from which the type
    will be inferred if not specified in the shorthand.

    Parameters
    ----------
    shorthand: str
        Shorthand string of the form "agg(col):typ"
    data : pd.DataFrame (optional)
        Dataframe from which to infer types

    Returns
    -------
    D : dict
        Dictionary which always contains a 'field' key, and additionally
        contains an 'aggregate' and 'type' key depending on the input.

    Examples
    --------
    >>> data = pd.DataFrame({'foo': ['A', 'B', 'A', 'B'],
    ...                      'bar': [1, 2, 3, 4]})

    >>> parse_shorthand('name')
    {'field': 'name'}

    >>> parse_shorthand('average(col)')  # doctest: +SKIP
    {'aggregate': 'average', 'field': 'col'}

    >>> parse_shorthand('foo:O')  # doctest: +SKIP
    {'field': 'foo', 'type': 'ordinal'}

    >>> parse_shorthand('min(foo):Q')  # doctest: +SKIP
    {'aggregate': 'min', 'field': 'foo', 'type': 'quantitative'}

    >>> parse_shorthand('foo', data)  # doctest: +SKIP
    {'field': 'foo', 'type': 'nominal'}

    >>> parse_shorthand('bar', data)  # doctest: +SKIP
    {'field': 'bar', 'type': 'quantitative'}

    >>> parse_shorthand('bar:O', data)  # doctest: +SKIP
    {'field': 'bar', 'type': 'ordinal'}

    >>> parse_shorthand('sum(bar)', data)  # doctest: +SKIP
    {'aggregate': 'sum', 'field': 'bar', 'type': 'quantitative'}

    >>> parse_shorthand('count()', data)  # doctest: +SKIP
    {'aggregate': 'count', 'type': 'quantitative'}
    """
    attrs = _parse_shorthand(shorthand)
    if isinstance(data, pd.DataFrame) and 'type' not in attrs:
        if 'field' in attrs and attrs['field'] in data.columns:
            attrs['type'] = infer_vegalite_type(data[attrs['field']])
    return attrs


def use_signature(Obj):
    """Apply call signature and documentation of Obj to the decorated method"""
    def decorate(f):
        # call-signature of f is exposed via __wrapped__.
        # we want it to mimic Obj.__init__
        f.__wrapped__ = Obj.__init__
        f._uses_signature = Obj

        # Supplement the docstring of f with information from Obj
        doclines = Obj.__doc__.splitlines()
        if f.__doc__:
            doc = f.__doc__ + '\n'.join(doclines[1:])
        else:
            doc = '\n'.join(doclines)
        try:
            f.__doc__ = doc
        except AttributeError:
            # __doc__ is not modifiable for classes in Python < 3.3
            pass
        return f
    return decorate


def update_subtraits(obj, attrs, **kwargs):
    """Recursively update sub-traits without overwriting other traits"""
    # TODO: infer keywords from args
    if not kwargs:
        return obj

    # obj can be a SchemaBase object or a dict
    if obj is Undefined:
        obj = dct = {}
    elif isinstance(obj, SchemaBase):
        dct = obj._kwds
    else:
        dct = obj

    if isinstance(attrs, six.string_types):
        attrs = (attrs,)

    if len(attrs) == 0:
        dct.update(kwargs)
    else:
        attr = attrs[0]
        trait = dct.get(attr, Undefined)
        if trait is Undefined:
            trait = dct[attr] = {}
        dct[attr] = update_subtraits(trait, attrs[1:], **kwargs)
    return obj


def update_nested(original, update, copy=False):
    """Update nested dictionaries

    Parameters
    ----------
    original : dict
        the original (nested) dictionary, which will be updated in-place
    update : dict
        the nested dictionary of updates
    copy : bool, default False
        if True, then copy the original dictionary rather than modifying it

    Returns
    -------
    original : dict
        a reference to the (modified) original dict

    Examples
    --------
    >>> original = {'x': {'b': 2, 'c': 4}}
    >>> update = {'x': {'b': 5, 'd': 6}, 'y': 40}
    >>> update_nested(original, update)  # doctest: +SKIP
    {'x': {'b': 5, 'c': 4, 'd': 6}, 'y': 40}
    >>> original  # doctest: +SKIP
    {'x': {'b': 5, 'c': 4, 'd': 6}, 'y': 40}
    """
    if copy:
        original = deepcopy(original)
    for key, val in update.items():
        if isinstance(val, collections.Mapping):
            orig_val = original.get(key, {})
            if isinstance(orig_val, collections.Mapping):
                original[key] = update_nested(orig_val, val)
            else:
                original[key] = val
        else:
            original[key] = val
    return original


def write_file_or_filename(fp, content, mode='w'):
    """Write content to fp, whether fp is a string or a file-like object"""
    if isinstance(fp, six.string_types):
        with open(fp, mode) as f:
            f.write(content)
    else:
        fp.write(content)


def display_traceback(in_ipython=True):
    exc_info = sys.exc_info()

    if in_ipython:
        from IPython.core.getipython import get_ipython
        ip = get_ipython()
    else:
        ip = None

    if ip is not None:
        ip.showtraceback(exc_info)
    else:
        traceback.print_exception(*exc_info)
