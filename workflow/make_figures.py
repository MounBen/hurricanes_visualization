from workflow.fixed_values import get_boundaries, get_gulf_stream, additional_legend
import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.themes import Theme
from bokeh.layouts import column, row
from bokeh.models.widgets import Panel, Tabs, Toggle, DataTable, TableColumn, DateFormatter
from bokeh.models import ColumnDataSource, WMTSTileSource, RangeSlider, Select, HoverTool


def make_start_end_figure(doc):
    """
    Creates a Bokeh app for visualizations of start and end of hurricanes
    """
    df_spawn_end = pd.read_csv('files/df_start_end_bokeh.csv', index_col=0)

    year_min, year_max, lon_boundaries, lat_boundaries = get_boundaries(df_spawn_end)

    gulf_stream_lon1, gulf_stream_lon2, gulf_stream_lat1, gulf_stream_lat2 = get_gulf_stream()

    # credits of the map
    url = 'http://a.basemaps.cartocdn.com/rastertiles/voyager/{Z}/{X}/{Y}.png'
    attribution = "Tiles by Carto, under CC BY 3.0. Data by OSM, under ODbL"

    add_paragraph = additional_legend(loc='tracks')

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
    toggle_month = Toggle(label="Show end points", button_type="success")
    toggle_dist_month = Toggle(label="Show distance traveled", button_type="success")

    # definition and configuration of the year and month sliders
    slider_year = RangeSlider(start=year_min, end=year_max,
                              value=(year_min, year_max), step=1, title="Years")

    slider_month = RangeSlider(start=1, end=12,
                               value=(1, 12), step=1, title="Months")

    # End points
    toggle_season = Toggle(label="Show end points", button_type="success")
    toggle_dist_season = Toggle(label="Show distance traveled", button_type="success")

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
            toggle_month.label = "Show end points"

        else:

            c2.visible, s1.visible = True, True
            toggle_month.label= "Unshow end points"

        if not dist:

            c1.visible, d1.visible = True, False
            toggle_dist_month.label = "Show distance traveled"

        else:

            c1.visible, d1.visible = False, True
            toggle_dist_month.label = "Unshow distance traveled"

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
            toggle_season.label = "Show end points"

        else:

            c4.visible, s2.visible = True, True
            toggle_season.label = "Show end points"

        if not dist:

            c3.visible, d2.visible = True, False
            toggle_dist_season.label = "Show distance traveled"

        else:

            c3.visible, d2.visible = False, True
            toggle_dist_season.label = "Unshow distance traveled"

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

        if tabs.active == 0:

            update_map_se('', '', '')

        else:

            update_map_season('', '', '')

    tabs.on_change('active', tab_change)

    # Make document
    doc.add_root(tabs)
    doc.title = 'Hurricanes'
    doc.theme = Theme(filename="theme.yaml")


def make_tracks_figure(doc):
    """
    Create a Bokeh app for visualization of the tracks of hurricanes
    """

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
    url = 'http://a.basemaps.cartocdn.com/rastertiles/voyager/{Z}/{X}/{Y}.png'
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
