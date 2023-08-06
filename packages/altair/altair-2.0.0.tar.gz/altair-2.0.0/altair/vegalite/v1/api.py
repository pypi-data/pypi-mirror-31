"""
Main API for Vega-lite spec generation.

DSL mapping Vega types to IPython traitlets.
"""
import six
import warnings

import jsonschema
import pandas as pd

from .schema import core, channels, Undefined, SCHEMA_URL

from .data import data_transformers, pipe
from ... import utils
from .display import renderers, VEGALITE_VERSION, VEGA_VERSION, VEGAEMBED_VERSION
from .theme import themes


def _get_channels_mapping():
    mapping = {}
    for attr in dir(channels):
        cls = getattr(channels, attr)
        if isinstance(cls, type) and issubclass(cls, core.SchemaBase):
            mapping[cls] = attr.lower()
    return mapping


# *************************************************************************
# Formula wrapper
# - makes field a required first argument of initialization
# - allows expr trait to be an Expression and processes it properly
# *************************************************************************

class Formula(core.Formula):
    def __init__(self, field, expr=Undefined, **kwargs):
        super(Formula, self).__init__(field=field, expr=expr, **kwargs)


# *************************************************************************
# Top-level Objects
# *************************************************************************

class TopLevelMixin(object):
    _class_is_valid_at_instantiation = False

    def _prepare_data(self):
        if isinstance(self.data, (dict, core.Data)):
            pass
        elif isinstance(self.data, pd.DataFrame):
            self.data = pipe(self.data, data_transformers.get())
        elif isinstance(self.data, six.string_types):
            self.data = core.Data(url=self.data)

    def to_dict(self, *args, **kwargs):
        copy = self.copy()
        original_data = getattr(copy, 'data', Undefined)
        copy._prepare_data()

        # We make use of two context markers:
        # - 'data' points to the data that should be referenced for column type
        #   inference.
        # - 'top_level' is a boolean flag that is assumed to be true; if it's
        #   true then a "$schema" arg is added to the dict.
        context = kwargs.get('context', {}).copy()

        is_top_level = context.get('top_level', True)
        context['top_level'] = False

        if original_data is not Undefined:
            context['data'] = original_data
        kwargs['context'] = context

        try:
            dct = super(TopLevelMixin, copy).to_dict(*args, **kwargs)
        except jsonschema.ValidationError:
            dct = None

        # If we hit an error, then re-convert with validate='deep' to get
        # a more useful traceback. We don't do this by default because it's
        # much slower in the case that there are no errors.
        if dct is None:
            kwargs['validate'] = 'deep'
            dct = super(TopLevelMixin, copy).to_dict(*args, **kwargs)

        if is_top_level:
            # since this is top-level we add $schema if it's missing
            if '$schema' not in dct:
                dct['$schema'] = SCHEMA_URL

            # apply theme from theme registry
            the_theme = themes.get()
            dct = utils.update_nested(the_theme(), dct, copy=True)
        return dct

    def savechart(self, fp, format=None, **kwargs):
        """Save a chart to file in a variety of formats

        Supported formats are json, html, png, svg

        Parameters
        ----------
        fp : string filename or file-like object
            file in which to write the chart.
        format : string (optional)
            the format to write: one of ['json', 'html', 'png', 'svg'].
            If not specified, the format will be determined from the filename.
        **kwargs :
            Additional keyword arguments are passed to the output method
            associated with the specified format.
        """
        warnings.warn(
            "Chart.savechart is deprecated in favor of Chart.save",
            DeprecationWarning
        )
        return self.save(fp, format=None, **kwargs)

    def save(self, fp, format=None, override_data_transformer=True, **kwargs):
        """Save a chart to file in a variety of formats

        Supported formats are json, html, png, svg

        Parameters
        ----------
        fp : string filename or file-like object
            file in which to write the chart.
        format : string (optional)
            the format to write: one of ['json', 'html', 'png', 'svg'].
            If not specified, the format will be determined from the filename.
        override_data_transformer : boolean (optional)
            If True (default), then the save action will be done with the
            default data_transformer with max_rows set to None. If False,
            then use the currently active data transformer.
        **kwargs :
            Additional keyword arguments are passed to the output method
            associated with the specified format.
        """
        from ...utils.save import save

        kwds = dict(chart=self, fp=fp, format=format,
                    vegalite_version=VEGALITE_VERSION,
                    vega_version=VEGA_VERSION,
                    vegaembed_version=VEGAEMBED_VERSION,
                    **kwargs)

        # By default we override the data transformer. This makes it so
        # that save() will succeed even for large datasets that would
        # normally trigger a MaxBinsError
        if override_data_transformer:
            with data_transformers.enable('default', max_rows=None):
                result = save(**kwds)
        else:
            result = save(**kwds)
        return result

    # transform method
    @utils.use_signature(core.Transform)
    def transform_data(self, **kwargs):
        """Set the data transform by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, 'transform', **kwargs)

    # Configuration methods
    @utils.use_signature(core.Config)
    def configure(self, **kwargs):
        """Set chart configuration"""
        copy = self.copy()
        return utils.update_subtraits(copy, 'config', **kwargs)

    @utils.use_signature(core.AxisConfig)
    def configure_axis(self, **kwargs):
        """Configure the chart's axes by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'axis'), **kwargs)

    @utils.use_signature(core.CellConfig)
    def configure_cell(self, **kwargs):
        """Configure the chart's cell's by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'cell'), **kwargs)

    @utils.use_signature(core.LegendConfig)
    def configure_legend(self, **kwargs):
        """Configure the chart's legend by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'legend'), **kwargs)

    @utils.use_signature(core.OverlayConfig)
    def configure_overlay(self, **kwargs):
        """Configure the chart's overlay by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'overlay'), **kwargs)

    @utils.use_signature(core.MarkConfig)
    def configure_mark(self, **kwargs):
        """Configure the chart's marks by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'mark'), **kwargs)

    @utils.use_signature(core.ScaleConfig)
    def configure_scale(self, **kwargs):
        """Configure the chart's scales by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'scale'), **kwargs)

    @utils.use_signature(core.FacetConfig)
    def configure_facet(self, **kwargs):
        """Configure the chart's scales by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'facet'), **kwargs)

    @utils.use_signature(core.AxisConfig)
    def configure_facet_axis(self, **kwargs):
        """Configure the facet's axes by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'facet', 'axis'),
                                      **kwargs)

    @utils.use_signature(core.CellConfig)
    def configure_facet_cell(self, **kwargs):
        """Configure the facet's cells by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'facet', 'cell'),
                                      **kwargs)

    @utils.use_signature(core.FacetGridConfig)
    def configure_facet_grid(self, **kwargs):
        """Configure the facet's grid by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'facet', 'grid'),
                                      **kwargs)

    @utils.use_signature(core.FacetScaleConfig)
    def configure_facet_scale(self, **kwargs):
        """Configure the facet's scales by keyword args."""
        copy = self.copy()
        return utils.update_subtraits(copy, ('config', 'facet', 'scale'),
                                      **kwargs)

    # Display related methods

    def _repr_mimebundle_(self, include, exclude):
        """Return a MIME bundle for display in Jupyter frontends."""
        # Catch errors explicitly to get around issues in Jupyter frontend
        # see https://github.com/ipython/ipython/issues/11038
        try:
            dct = self.to_dict()
        except Exception:
            utils.display_traceback(in_ipython=True)
            return {}
        else:
            return renderers.get()(dct)


class Chart(TopLevelMixin, core.ExtendedUnitSpec):
    def __init__(self, data=Undefined, encoding=Undefined, mark=Undefined,
                 **kwargs):
        super(Chart, self).__init__(data=data, encoding=encoding, mark=mark,
                                    **kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_area(self, **kwargs):
        """Set the mark to 'area' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'area'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_bar(self, **kwargs):
        """Set the mark to 'bar' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'bar'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_errorBar(self, **kwargs):
        """Set the mark to 'errorBar' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'errorBar'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_line(self, **kwargs):
        """Set the mark to 'line' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'line'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_point(self, **kwargs):
        """Set the mark to 'point' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'point'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_rule(self, **kwargs):
        """Set the mark to 'rule' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'rule'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_text(self, **kwargs):
        """Set the mark to 'text' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'text'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_tick(self, **kwargs):
        """Set the mark to 'tick' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'tick'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_circle(self, **kwargs):
        """Set the mark to 'circle' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'circle'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.MarkConfig)
    def mark_square(self, **kwargs):
        """Set the mark to 'square' and optionally specify mark properties"""
        copy = self.copy()
        copy.mark = 'square'
        return copy.configure_mark(**kwargs)

    @utils.use_signature(core.Encoding)
    def encode(self, *args, **kwargs):
        """Define the encoding for the Chart."""
        if args:
            mapping = _get_channels_mapping()
            for arg in args:
                encoding = mapping.get(type(arg), None)
                if encoding is None:
                    raise NotImplementedError("non-keyword arg of type {0}"
                                              "".format(type(arg)))
                if encoding in kwargs:
                    raise ValueError("encode: encoding {0} specified twice"
                                     "".format(encoding))
                kwargs[encoding] = arg

        for prop, field in list(kwargs.items()):
            if not isinstance(field, core.SchemaBase):
                cls = getattr(channels, prop.title())
                # Don't validate now, because field will be computed
                # as part of the to_dict() call.
                kwargs[prop] = cls.from_dict(field, validate=False)
        return utils.update_subtraits(self, 'encoding', **kwargs)
