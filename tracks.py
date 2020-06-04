from workflow.fixed_values import get_boundaries, get_gulf_stream, additional_legend
import numpy as np
import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.themes import Theme
from bokeh.layouts import column, row
from bokeh.models.widgets import DataTable, TableColumn, DateFormatter
from bokeh.models import ColumnDataSource, WMTSTileSource, RangeSlider, Select, HoverTool


"""
Create a Bokeh app for visualization of the tracks of hurricanes
"""
doc =curdoc()

df = pd.read_csv('files/df_full_tracks_bokeh.csv', index_col=0, parse_dates=['Time'])

# Remove last entry for each hurricane, add steps numbering, year_start, year_end, zone start
df.dropna(subset=['x_end'], inplace=True)

df.sort_values(by=['ID', 'Time'], inplace=True)

steps = df.groupby(by='ID').Time.count()
times = df.groupby(by='ID').Time.first()
zones = df.groupby(by='ID').Zones.first()

df['Step'] = [i for hur in steps.index for i in range(steps[hur])]
df['Year_start'] = [times[hur].year for hur in steps.index for i in range(steps[hur])]
df['Month_start'] = [times[hur].month for hur in steps.index for i in range(steps[hur])]
df['Zones_start'] = [zones[hur]for hur in steps.index for i in range(steps[hur])]

# Convert knots to km/h
df['Max_Speed'] = df['Max_Speed'] * 1.852

# -----------------------------------------------------
# FIGURE
# -----------------------------------------------------
year_min, year_max, lon_boundaries, lat_boundaries = get_boundaries(df)

gulf_stream_lon1, gulf_stream_lon2, gulf_stream_lat1, gulf_stream_lat2 = get_gulf_stream()

# credits of the map
url = 'https://a.basemaps.cartocdn.com/rastertiles/voyager/{Z}/{X}/{Y}.png'
attribution = "Tiles by Carto, under CC BY 3.0. Data by OSM, under ODbL"

add_paragraph = additional_legend(loc='spawns')

# -----------------------------------------------------
# WIDGETS
# -----------------------------------------------------

# definition and configuration of the number selection
options_number = ['-1'] + [str(x) for x in list(np.arange(1, 21))]
select_number = Select(title='Number of hurricanes:', value='5', options=options_number)

# definition and configuration of the zone selection
options_zone = ['All', 'Mexico_Caribbean', 'Atlantic']
select_zone = Select(title='Spawning Zone:', value='All', options=options_zone)

# definition and configuration of the year and month sliders
slider_year = RangeSlider(start=year_min, end=year_max,
                          value=(year_min, year_max), step=1, title="Years")

slider_month = RangeSlider(start=1, end=12,
                           value=(1, 12), step=1, title="Months")

# definition and configuration of the number selection
# select_number_season = Select(title='Number of hurricanes:', value='5',
#                              options=options_number)

# definition and configuration of the zone selection
# select_zone_season = Select(title='Spawning Zone:', value='All', options=options_zone)

# definition and configuration of the year and sliders
# slider_year_season = RangeSlider(start=year_min, end=year_max,
#                                 value=(year_min, year_max), step=1, title="Years")

# definition and configuration of the season selection
# options_season = ['All', 'Winter', 'Spring', 'Summer', 'Autumn']
# select_season = Select(title='Season:', value='All', options=options_season)

# -------------------------------------------------------
# DATA SOURCE AND RANDOMIZATION
# -------------------------------------------------------
np.random.seed(42)
n = 5

select_list = list(np.random.choice(df.ID.unique(), size=n, replace=False))
filtr = df.ID.map(lambda x: x in select_list)

source = ColumnDataSource(data=df[filtr])

# Initialization of the map
p = figure(tools='pan, wheel_zoom', x_range=(lon_boundaries[0], lon_boundaries[1]),
           y_range=(lat_boundaries[0], lat_boundaries[1]),
           x_axis_type="mercator", y_axis_type="mercator")

p.add_tile(WMTSTileSource(url=url, attribution=attribution))

# Add data points
# - Start
# - End
# - Start with size adjusted to the traveled distance
c1 = p.circle(x='x_start', y='y_start', fill_color='green', size=5, source=source)

c2 = p.circle(x='x_end', y='y_end', fill_color='green', size=5, source=source)

# Line between start and end points
s1 = p.segment(x0='x_start', y0='y_start', x1='x_end', y1='y_end',
               line_dash='dashed', source=source)

# Configuration of the hovertool
hover = HoverTool(tooltips=[("ID", "@ID"), ("Step", "@Step"), ("Distance", "@Distance")], renderers=[c1])
p.tools.append(hover)

# Draw the Gulf Stream
p.segment(x0=gulf_stream_lon1[:-1], y0=gulf_stream_lat1[:-1],
          x1=gulf_stream_lon1[1:], y1=gulf_stream_lat1[1:],
          legend_label='Gulf Stream', color='red', line_alpha=0.5, line_width=2)

p.segment(x0=gulf_stream_lon2[:-1], y0=gulf_stream_lat2[:-1],
          x1=gulf_stream_lon2[1:], y1=gulf_stream_lat2[1:],
          color='red', line_alpha=0.5, line_width=2)

p.legend.location = "top_left"

# DataFrame display
no_cols = ['x_start', 'x_end', 'y_start', 'y_end', 'Zones_start', 'ID', 'Time']
cols = ([TableColumn(field='ID', title='ID')]
        + [TableColumn(field='Time', title='Time', formatter=DateFormatter(format="%d/%m/%Y %H:%M"))]
        + [TableColumn(field=col, title=col) for col in df.columns if col not in no_cols])
data_table = DataTable(columns=cols, source=source, width=1100, selectable=False)

# updating process of the data underlying the map depending on user actions.
def update_map_se(attr, old, new):

    yr = slider_year.value
    month = slider_month.value
    zone = select_zone.value
    n = select_number.value
    n = int(n)

    if zone == 'All':
        df_temp = df.loc[(df['Year_start'] >= yr[0])
                         & (df['Year_start'] <= yr[1])
                         & (df['Month_start'] >= month[0])
                         & (df['Month_start'] <= month[1])]

    else:
        df_temp = df.loc[(df.Zones_start == zone)
                         & (df['Year_start'] >= yr[0])
                         & (df['Year_start'] <= yr[1])
                         & (df['Month_start'] >= month[0])
                         & (df['Month_start'] <= month[1])]

    if n == -1:

        source.data = ColumnDataSource.from_df(df_temp)
    else:

        if n > len(df_temp):  # For cases where there are not enough data points
            n = int(len(df_temp))

        select_list = list(np.random.choice(df_temp.ID.unique(), size=n, replace=False))

        filtr = df_temp.ID.map(lambda x: x in select_list)

        source.data = ColumnDataSource.from_df(df_temp.loc[filtr])

# activation of the changes on user action
select_number.on_change('value', update_map_se)
slider_year.on_change('value', update_map_se)
slider_month.on_change('value', update_map_se)
select_zone.on_change('value', update_map_se)

layout = column(row(column(slider_year, slider_month, select_number, select_zone),
                    p, add_paragraph), data_table)

# Make document
doc.add_root(layout)
doc.title = 'Hurricanes_Tracks'
doc.theme = Theme(filename="theme.yaml")
