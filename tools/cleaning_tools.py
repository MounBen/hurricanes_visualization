import pandas as pd


def format_date_hours(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format time and remove data points outside the 6-hourly scheme.
    
    Parameters
    ----------
    df : pd.DataFrame
        The tracks DataFrame.
    
    Return
    -------
    df_temp : pd.DataFrame
        A copy of df with a proper datetime column, in format %Y-%m-%d, with hours 06:00, 12:00, 18:00, 00:00 only.
    """

    df_temp = df.copy()

    df_temp['Date'] = df_temp['Date'].astype(str)
    df_temp['Date'] = df_temp['Date'].map(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:])
    df_temp['Hour'] = df_temp['Hour'].map(lambda x: x[1:3] + ':' + x[3:])
    df_temp['Time'] = df_temp['Hour'] + ' ' + df_temp['Date']
    df_temp['Time'] = df_temp['Time'].map(lambda x: pd.to_datetime(x))

    # Extraction of the 6-hourly scheme
    hours = ['06:00', '12:00', '18:00', '00:00']

    filt = df_temp.Hour.map(lambda x: x in hours)

    df_temp = df_temp.loc[filt]

    df_temp.reset_index(drop=True, inplace=True)

    # Reality Check
    if set(df_temp.Hour.unique()) != set(hours):
        raise ValueError('The extraction of the 6-hourly scheme failed.')

    df_temp.drop(columns=['Date', 'Hour'], inplace=True)

    return df_temp


def fill_radii(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove some missing values from radii columns of `df`.

    By definition a low (resp. med, high) `wind radius` is the maximal distance
    from the center of the hurricane where winds stronger than 34 (resp. 50, 64) knots
    were observed.

    We use this definition to fill some missing values. E.g. if the `Max_Speed`is lower
    than 34 knots, all radii have to be 0.

    Parameters
    ----------
    df : pd.DataFrame
        The tracks DataFrame.

    Return
    -------
    df_temp : pd.DataFrame
        A copy of df with partially completed missing values for the radii columns.
    """

    df_temp = df.copy()

    # We extract the names of the columns corresponding to radii
    rad_cols = [col for col in df_temp.columns if 'Rad' in col]
    speeds = [0, 34, 50, 64]

    # For each of the three speeds relevant to wind radii, we create a dictionary setting some radii to 0.

    # For speeds lower than 34, all radii are set to 0.
    dict_low = {col: 0.0 for col in rad_cols}

    # For speeds lower than 50, greater than 34, medium and high radii are set to 0.
    dict_med = {col: 0.0 for col in rad_cols[4:]}

    # For speeds lower than 64, greater than 50, high radii are set to 0.
    dict_high = {col: 0.0 for col in rad_cols[8:]}

    dicts = [dict_low, dict_med, dict_high]

    for i in range(len(speeds) - 1):
        filt = (df_temp.Max_Speed > speeds[i]) & (df_temp.Max_Speed <= speeds[i + 1])

        df_temp.loc[filt] = df_temp.loc[filt].fillna(dicts[i])

    return df_temp


def format_lon_lat(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format longitude and latitude values from strings to integers.

    Longitudes as strings are given in a format `mI` where m is a number and I
    is either `W` (west) or `E` (east) with respect to the Greenwich meridian.
    West coordinates are meant to be negative and east are positive.

    Latitudes as strings are given in a format `mI` where m is a number and I
    is either `N` (north) or `S` (south) with respect to the equator.
    South coordinates are meant to be negative and north are positive.

    Parameters
    ----------
    df : pd.DataFrame
        The tracks DataFrame.

    Return
    -------
    df_temp : pd.DataFrame
        A copy of df with proper longitudes and latitudes.
    """

    df_temp = df.copy()

    df_temp.Longitude = df_temp.Longitude.map(lambda x: -1*float(x[:-1]) if x[-1] == 'W' else float(x[:-1]))
    df_temp.Latitude = df_temp.Latitude.map(lambda x: -1*float(x[:-1]) if x[-1] == 'S' else float(x[:-1]))

    return df_temp


def cleaning_pipeline(files_dir: str, track_name: str = 'df_tracks.csv',
                      new_name: str = 'df_tracks_after_1970', year: int = 1970):
    """
    Cleans the data from df_tracks and saves the data with year >= `year`into a separate DataFrame.

    Parameters
    ----------

    files_dir: str
        Path to the directory which contains the df_tracks DataFrame.
    track_name: str
        Name of the file containing df_tracks.
    new_name: str
        Name to use for saving the filtered data.
    year: int
        The year to use as a lower bound

    Return
    ------
    """
    tracks_path = files_dir + track_name

    # Necessary to set the dtype of Hour column, otherwise pandas infers int which yields errors
    df_tracks = pd.read_csv(tracks_path, header=0, index_col=0, dtype={'Hour': str})

    print(df_tracks.head())
    print('\n')

    df_tracks = format_date_hours(df_tracks)

    df_tracks = format_lon_lat(df_tracks)

    df_tracks = fill_radii(df_tracks)

    df_tracks = df_tracks.loc[df_tracks.Time.map(lambda x: x.year) >= year]

    df_tracks.reset_index(inplace=True, drop=True)

    save_path = files_dir + new_name + '.csv'
    df_tracks.to_csv(save_path)

    print(df_tracks.info())
    print('\n')
    print('There are {} missing values remaining.'.format(df_tracks.isnull().sum().sum()))



