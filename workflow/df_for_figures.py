import pandas as pd
from tools.features_engineering_tools import haversine


def create_full_tracks_df(file_path: str, file_name: str = '../files/df_full_tracks_bokeh.csv'):

    df_temp = pd.read_csv(file_path, index_col=0, dtype={'Hour': str}, parse_dates=['Time'])

    # Remove columns not used in the bokeh figures.
    cols = [col for col in df_temp.columns if 'Rad' in col] + ['Min_Pressure']

    df_temp.drop(columns=cols, inplace=True)

    # Shift main columns by -1 to compute distance etc
    df_temp_2 = df_temp.groupby(by='ID')[['Longitude', 'Latitude', 'x', 'y']].shift(-1)

    df_temp = df_temp.merge(df_temp_2, left_index=True, right_index=True, suffixes=('_start', '_end'))

    # Computes distance for two consecutive data points
    df_temp = haversine(df_temp)

    df_temp['Avg_Speed'] = df_temp.Distance/6.0

    # Re-ordering the columns
    df_temp = df_temp[['ID', 'Time', 'Status', 'Latitude_start', 'Longitude_start', 'Latitude_end',
                       'Longitude_end', 'Distance', 'Max_Speed', 'Avg_Speed', 'Season', 'Zones',
                       'x_start', 'y_start', 'x_end', 'y_end']]

    df_temp.to_csv(file_name)


def create_start_end_df(file_path: str, file_name: str = '../files/df_start_end_bokeh.csv'):

    df_temp = pd.read_csv(file_path, index_col=0, dtype={'Hour': str}, parse_dates=['Time'])

    # Keep only the desired columns
    df_temp.drop(columns=['Status', 'Latitude_end', 'Longitude_end', 'Max_Speed',
                          'Avg_Speed', 'x_end', 'y_end'], inplace=True)

    # Rename columns for convenience
    df_temp.rename(columns={'Longitude_start': 'Longitude', 'Latitude_start': 'Latitude',
                            'x_start': 'x', 'y_start': 'y'}, inplace=True)

    # Compute the total distances for each hurricanes, save into a pd.Series, drop the distance column
    df_temp.Distance.fillna(0, inplace=True)
    dist = df_temp.groupby(by='ID').Distance.sum()
    df_temp.drop(columns=['Distance'], inplace=True)

    # Add Year and Columns
    df_temp['Year'] = df_temp.Time.map(lambda x: x.year)
    df_temp['Month'] = df_temp.Time.map(lambda x: x.month)

    # Separate first and last entry for each ID
    df_start = df_temp.drop_duplicates(subset='ID', keep='first')

    df_end = df_temp.drop_duplicates(subset='ID', keep='last')

    # Merge both together
    df_start_end_bokeh = df_start.merge(df_end, on='ID', suffixes=('_start', '_end'))

    # Add duration column
    df_start_end_bokeh['Duration'] = (
                                    df_start_end_bokeh['Time_end'] - df_start_end_bokeh['Time_start']
                                    ).map(lambda x: x.total_seconds()/(24*3600)).astype(str)

    df_start_end_bokeh['Duration'] = df_start_end_bokeh['Duration'] + ' days'

    df_start_end_bokeh.drop(columns=['Time_end', 'Time_start'], inplace=True)

    # Add distance column and distance draw for bokeh
    df_start_end_bokeh = df_start_end_bokeh.merge(dist, on='ID')
    df_start_end_bokeh['Distance_draw'] = 42 * df_start_end_bokeh['Distance']

    df_start_end_bokeh.to_csv(file_name)

    print(df_start_end_bokeh.head(10))
    print(df_start_end_bokeh.columns)
