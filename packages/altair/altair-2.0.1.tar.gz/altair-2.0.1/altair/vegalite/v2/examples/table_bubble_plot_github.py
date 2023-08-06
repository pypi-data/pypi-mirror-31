"""
Table Bubble Plot (Github Punch Card)
-------------------------------------
This example shows github contributions by the day of week and hour of the day.
"""
# category: scatter plots
import altair as alt
from vega_datasets import data

source = data.github.url

alt.Chart(source).mark_circle().encode(
    alt.X('time:O', timeUnit='hours'),
    alt.Y('time:O', timeUnit='day'),
    size='sum(count):Q'
)
