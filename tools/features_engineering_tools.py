import pandas as pd
import numpy as np


def wgs84_to_web_mercator(df: pd.DataFrame, lon: str = "Longitude", lat: str = "Latitude") -> pd.DataFrame:
    """
    Converts latitude and longitudes to web mercator format (used by bokeh)

    Parameters
    ----------

    df : pd.DataFrame
        A DataFrame containing geographical data expressed in longitudes and latitudes.
    lon: str
        The column of df containing the longitudes.
    lat: str
        The column of df containing the latitudes.

    Return
    ------

    df_temp: pd.DataFrame
        A copy of df, with two additional columns containing the web mercator coordinates

    """

    df_temp = df.copy()

    k = 6378137
    df_temp["x"] = df_temp[lon] * (k * np.pi/180.0)
    df_temp["y"] = np.log(np.tan((90 + df_temp[lat]) * np.pi/360.0)) * k

    return df_temp


def season(df: pd.DataFrame, col: str = 'Time') -> pd.DataFrame:
    """
    Adds a column to df with the season corresponding the date of each entry.

    Parameters
    ----------

    df : pd.DataFrame
        A DataFrame containing a pd.datetime column
    col: str
        The column of df containing the date

    Return
    ------

    df_temp: pd.DataFrame
        A copy of df with an additional column for the season.

    """

    df_temp = df.copy()

    season_dict = {12: 'Winter', 1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 5: 'Spring',
                   6: 'Summer', 7: 'Summer', 8: 'Summer', 9: 'Autumn', 10: 'Autumn', 11: 'Autumn'}

    df_temp['Season'] = df_temp[col].map(lambda x: x.month).map(lambda x: season_dict[x])

    return df_temp


def zones(df: pd.DataFrame, lon: str = 'Longitude', lat: str = 'Latitude') -> pd.DataFrame:
    """
    Adds to df a column containing the Zone of each data point.

    There are two possible zones: Gulf of Mexico and Atlantic.

    Parameters
    ----------

    df : pd.DataFrame
        A DataFrame containing geographical data
    lon: str
        The column if df containing longitudes
    lat: str
        The column if df containing latitudes

    Return
    ------

    df_temp: pd.DataFrame
        A copy of df with the additional column `Zones`

    """

    df_temp = df.copy()

    # Arbitrary limit of the zones, follows the natural barrier of islands (Cuba, etc...)
    df_temp['Vertical'] = df_temp[lon] < -61
    df_temp['Cuba_Gua'] = df_temp[lat] + 6 / 19 * df_temp[lon] < -3.3
    df_temp['Flo_Cuba'] = df_temp[lat] + 6 * df_temp[lon] < -458

    df_temp['Zones'] = (df_temp.Vertical & df_temp.Cuba_Gua) | df_temp.Flo_Cuba

    df_temp.drop(columns=['Vertical', 'Cuba_Gua', 'Flo_Cuba'], inplace=True)

    df_temp.Zones.replace({True: 'Mexico_Caribbean', False: 'Atlantic'}, inplace=True)

    return df_temp


def haversine(df, lon_base: str = 'Longitude_start', lat_base: str ='Latitude_start',
              lon_s: str = 'Longitude_end', lat_s: str = 'Latitude_end',
              name: str = 'Distance') -> pd.DataFrame:
    """
    Computed the distance between two pairs of longitude/latitudes using the haversine formula.

    Parameters
    ----------

    df : pd.DataFrame
        A DataFrame containing pairs of longitude and latitudes.
    lon_base: str
        The column with the longitude of the first pair of coordinates.
    lat_base: str
        The column with the latitude of the first pair of coordinates.
    lon_s: str
        The column with the longitude of the second pair of coordinates.
    lat_s: str
        The column with the latitude of the second pair of coordinates.
    name: str
        The name of the new column that will contain the distance (in km).

    Return
    ------

    df_temp: pd.DataFrame
        A copy of df with the additional column `name` that contains the distance (in km).

    """

    df_temp = df.copy()

    r = 6371

    ratio = np.pi/360

    lat_sine = np.sin((df_temp[lat_s] - df_temp[lat_base]) * ratio)

    lat_cosines = np.cos(df_temp[lat_base] * ratio) * np.cos(df_temp[lat_s] * ratio)

    lon_sine = np.sin((df_temp[lon_s] - df_temp[lon_base]) * ratio)

    df_temp[name] = 2 * r * np.arcsin(np.sqrt(lat_sine ** 2 + lat_cosines * lon_sine ** 2))

    return df_temp
