from workflow.fixed_values import get_boundaries, get_gulf_stream, additional_legend
import numpy as np
import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.themes import Theme
from bokeh.layouts import column, row
from bokeh.models.widgets import Panel, Tabs, Toggle, DataTable, TableColumn
from bokeh.models import ColumnDataSource, WMTSTileSource, RangeSlider, Select, HoverTool



"""
Creates a Bokeh app for visualizations of start and end of hurricanes
"""
doc = curdoc()

df_spawn_end = pd.read_csv('files/df_start_end_bokeh.csv', index_col=0)

year_min, year_max, lon_boundaries, lat_boundaries = get_boundaries(df_spawn_end)

gulf_stream_lon1, gulf_stream_lon2, gulf_stream_lat1, gulf_stream_lat2 = get_gulf_stream()

# credits of the map
url = 'http://a.basemaps.cartocdn.com/rastertiles/voyager/{Z}/{X}/{Y}.png'
attribution = "Tiles by Carto, under CC BY 3.0. Data by OSM, under ODbL"

extra_txt = """
The Distance column here gives the total distance traveled by the hurricane, not the distance between
start and end points.
"""

add_paragraph = additional_legend(loc='tracks', extra_txt=extra_txt)

# -----------------------------------------------------
# WIDGETS
# -----------------------------------------------------

# definition and configuration of the number selection
options_number = ['-1'] + [str(x) for x in list(np.arange(1, 21))]
select_number = Select(title='Number of hurricanes:', value='5', options=options_number)

# definition and configuration of the zone selection
options_zone = ['All', 'Mexico_Caribbean', 'Atlantic']
select_zone = Select(title='Spawning Zone:', value='All', options=options_zone)

# Definition of buttons for end points and distances
toggle_month = Toggle(label="End points", button_type="success")
toggle_dist_month = Toggle(label="Distance", button_type="success")

# definition and configuration of the year and month sliders
slider_year = RangeSlider(start=year_min, end=year_max,
                          value=(year_min, year_max), step=1, title="Years")

slider_month = RangeSlider(start=1, end=12,
                           value=(1, 12), step=1, title="Months")

# End points
toggle_season = Toggle(label="End points", button_type="success")
toggle_dist_season = Toggle(label="Distance", button_type="success")

# definition and configuration of the number selection
select_number_season = Select(title='Number of hurricanes:', value='5',
                              options=options_number)

# definition and configuration of the zone selection
select_zone_season = Select(title='Spawning Zone:', value='All', options=options_zone)

# definition and configuration of the year and sliders
slider_year_season = RangeSlider(start=year_min, end=year_max,
                                 value=(year_min, year_max), step=1, title="Years")

# definition and configuration of the season selection
options_season = ['All', 'Winter', 'Spring', 'Summer', 'Autumn']
select_season = Select(title='Season:', value='All', options=options_season)

# -------------------------------------------------------
# DATA SOURCE AND RANDOMIZATION
# -------------------------------------------------------
np.random.seed(42)
n = 5

select_list = list(np.random.choice(df_spawn_end.index, size=n, replace=False))
filtr = df_spawn_end.index.map(lambda x: x in select_list)

source = ColumnDataSource(data=df_spawn_end[filtr])

# --------------------------------------------------------
# FIRST TAB
# --------------------------------------------------------

# Initialization of the map
p = figure(tools='pan, wheel_zoom', x_range=(lon_boundaries[0], lon_boundaries[1]),
           y_range=(lat_boundaries[0], lat_boundaries[1]),
           x_axis_type="mercator", y_axis_type="mercator")

p.add_tile(WMTSTileSource(url=url, attribution=attribution))

# Add data points
# - Start
# - End
# - Start with size adjusted to the traveled distance
c1 = p.circle(x='x_start', y='y_start', fill_color='green', size=8,
              source=source, legend_label='Start points')

c2 = p.circle(x='x_end', y='y_end', fill_color='orange', size=8,
              source=source, legend_label='End points')

d1 = p.circle(x='x_start', y='y_start', fill_color='green', radius='Distance_draw',
              source=source)

# Line between start and end points
s1 = p.segment(x0='x_start', y0='y_start', x1='x_end', y1='y_end',
               line_dash='dashed', source=source)

# Initial configuration of WIDGETS  for FIRST TAB
# - Don't show end points
# - Don't show segments between start and end points
# - Uniform size for starting points
c2.visible, s1.visible, d1.visible = False, False, False

# Configuration of the hovertool
hover = HoverTool(tooltips=[("ID", "@ID"), ("Duration", "@Duration"),
                            ("Distance", "@Distance")],
                  renderers=[c1, c2, d1], formatters={'Duration': 'printf'})
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
no_cols = ['x_start', 'x_end', 'y_start', 'y_end', 'Distance_draw']
cols = [TableColumn(field=col, title=col) for col in df_spawn_end.columns if col not in no_cols]
data_table = DataTable(columns=cols, source=source, width=1100, selectable=False)

# ------------------------------------------------------------------------
# UPDATING FIRST TAB
# ------------------------------------------------------------------------

# updating process of the data underlying the map depending on user actions.
def update_map_se(attr, old, new):

    yr = slider_year.value
    month = slider_month.value
    zone = select_zone.value
    n = select_number.value
    n = int(n)

    if zone == 'All':
        df_temp = df_spawn_end.loc[(df_spawn_end['Year_start'] >= yr[0])
                                   & (df_spawn_end['Year_start'] <= yr[1])
                                   & (df_spawn_end['Month_start'] >= month[0])
                                   & (df_spawn_end['Month_start'] <= month[1])]

    else:
        df_temp = df_spawn_end.loc[(df_spawn_end.Zones_start == zone)
                                   & (df_spawn_end['Year_start'] >= yr[0])
                                   & (df_spawn_end['Year_start'] <= yr[1])
                                   & (df_spawn_end['Month_start'] >= month[0])
                                   & (df_spawn_end['Month_start'] <= month[1])]

    if n == -1:

        source.data = ColumnDataSource.from_df(df_temp)
    else:

        if n > len(df_temp):  # For cases where there are not enough data points
            n = int(len(df_temp))

        select_list = list(np.random.choice(df_temp.index, size=n, replace=False))

        filtr = df_temp.index.map(lambda x: x in select_list)

        source.data = ColumnDataSource.from_df(df_temp.loc[filtr])

def month_active(atrr, old, new):

    active = toggle_month.active
    dist = toggle_dist_month.active

    if not active:

        c2.visible, s1.visible = False, False

    else:

        c2.visible, s1.visible = True, True

    if not dist:

        c1.visible, d1.visible = True, False

    else:

        c1.visible, d1.visible = False, True

# activation of the changes on user action
select_number.on_change('value', update_map_se)
slider_year.on_change('value', update_map_se)
slider_month.on_change('value', update_map_se)
select_zone.on_change('value', update_map_se)
toggle_month.on_change('active', month_active)
toggle_dist_month.on_change('active', month_active)

# Make first tab
tab_month = Panel(child=column(row(column(slider_year, slider_month,
                                   select_number, select_zone,
                                   toggle_month, toggle_dist_month), p, add_paragraph), data_table), title="Monthly")

# ----------------------------------------------------------------------------
# SECOND TAB
# ----------------------------------------------------------------------------

p_season = figure(tools='pan, wheel_zoom', x_range=(lon_boundaries[0], lon_boundaries[1]),
                  y_range=(lat_boundaries[0], lat_boundaries[1]),
                  x_axis_type="mercator", y_axis_type="mercator")

p_season.add_tile(WMTSTileSource(url=url, attribution=attribution))

# Add data points
# - Start
# - End
# - Start with size adjusted to the traveled distance
c3 = p_season.circle(x='x_start', y='y_start', fill_color='green', size=8,
                     source=source, legend_label='Start points')

c4 = p_season.circle(x='x_end', y='y_end', fill_color='orange', size=8,
                     source=source, legend_label='End points')

d2 = p_season.circle(x='x_start', y='y_start', fill_color='green', radius='Distance_draw',
                     source=source)

# line between start and end points
s2 = p_season.segment(x0='x_start', y0='y_start', x1='x_end', y1='y_end',
                      line_dash='dashed', source=source)

# Initial configuration of WIDGETS  for SECOND TAB
# - Don't show end points
# - Don't show segments between start and end points
# - Uniform size for starting points
c4.visible, s2.visible, d2.visible = False, False, False

# Configuration of the hovertool
hover_season = HoverTool(tooltips=[("ID", "@ID"), ("Duration", "@Duration"),
                                   ("Distance", "@Distance")],
                         renderers=[c3, c4], formatters={'Duration': 'printf'})
p_season.tools.append(hover_season)

# Gulf Stream
p_season.segment(x0=gulf_stream_lon1[:-1], y0=gulf_stream_lat1[:-1],
                 x1=gulf_stream_lon1[1:], y1=gulf_stream_lat1[1:],
                 legend_label='Gulf Stream', color='red', line_alpha=0.5, line_width=2)

p_season.segment(x0=gulf_stream_lon2[:-1], y0=gulf_stream_lat2[:-1],
                 x1=gulf_stream_lon2[1:], y1=gulf_stream_lat2[1:],
                 color='red', line_alpha=0.5, line_width=2)

p_season.legend.location = "top_left"

# ------------------------------------------------------------------------
# UPDATING SECOND TAB
# ------------------------------------------------------------------------

# updating process of the data underlying the map depending on user actions.
def update_map_season(attr, old, new):

    yr = slider_year_season.value
    season = select_season.value
    zone = select_zone_season.value
    n = select_number_season.value
    n = int(n)

    if (zone == 'All') & (season == 'All'):
        df_temp = df_spawn_end.loc[(df_spawn_end['Year_start'] >= yr[0])
                                   & (df_spawn_end['Year_start'] <= yr[1])]

    elif (zone != 'All') & (season == 'All'):
        df_temp = df_spawn_end.loc[(df_spawn_end.Zones_start == zone)
                                   & (df_spawn_end['Year_start'] >= yr[0])
                                   & (df_spawn_end['Year_start'] <= yr[1])]

    elif (zone == 'All') & (season != 'All'):
        df_temp = df_spawn_end.loc[(df_spawn_end.Season_start == season)
                                   & (df_spawn_end['Year_start'] >= yr[0])
                                   & (df_spawn_end['Year_start'] <= yr[1])]

    else:
        df_temp = df_spawn_end.loc[(df_spawn_end.Zones_start == zone)
                                   & (df_spawn_end.Season_start == season)
                                   & (df_spawn_end['Year_start'] >= yr[0])
                                   & (df_spawn_end['Year_start'] <= yr[1])]

    if n == -1:

        source.data = ColumnDataSource.from_df(df_temp)
    else:

        if n > len(df_temp):  # For cases where there are not enough data points
            n = int(len(df_temp))

        select_list = list(np.random.choice(df_temp.index, size=n, replace=False))

        filtr = df_temp.index.map(lambda x: x in select_list)

        source.data = ColumnDataSource.from_df(df_temp.loc[filtr])

def season_active(atrr, old, new):
    active = toggle_season.active
    dist = toggle_dist_season.active

    if not active:

        c4.visible, s2.visible = False, False

    else:

        c4.visible, s2.visible = True, True

    if not dist:

        c3.visible, d2.visible = True, False
    else:

        c3.visible, d2.visible = False, True

select_number_season.on_change('value', update_map_season)
slider_year_season.on_change('value', update_map_season)
select_season.on_change('value', update_map_season)
select_zone_season.on_change('value', update_map_season)
toggle_season.on_change('active', season_active)
toggle_dist_season.on_change('active', season_active)

# Make second tab
tab_season = Panel(child=column(row(column(slider_year_season, select_number_season, select_season,
                                    select_zone_season,toggle_season, toggle_dist_season),
                                    p_season, add_paragraph), data_table), title="Seasonal")

# ----------------------------------------------------------------------------
# FINAL SET UP
# ----------------------------------------------------------------------------

tabs = Tabs(tabs=[tab_month, tab_season])

def tab_change(atrr, old, new):

    n = 5

    select_list = list(np.random.choice(df_spawn_end.index, size=n, replace=False))

    filter = df_spawn_end.index.map(lambda x: x in select_list)

    source.data = ColumnDataSource.from_df(df_spawn_end.loc[filter])

tabs.on_change('active', tab_change)

# Make document
doc.add_root(tabs)
doc.title = 'Hurricanes'
doc.theme = Theme(filename="theme.yaml")