import numpy as np
import pandas as pd
from typing import Tuple, List
from bokeh.models import Div


def get_boundaries(df: pd.DataFrame, year: str='Year_start',
                   lon: str = 'Longitude_start', lat: str = 'Latitude_start')\
                    -> Tuple[int, int, List[float], List[float]]:
    """
    Returns the time and geographical boundaries for the data in df.


    Parameters
    ----------

    df : pd.DataFrame
        A DataFrame containing time and latitude/longitude data.
    year : str
        Refers to the time column of df.
    lon : str
        Refers to the longitude column of df.
    lat : str
        Refers to the latitude column of df.

    Returns
    -------

    year_min : int
        The lowest year in the data.
    year_max : int
        The highest year in the data.
    lon_boundaries : List[float]
        The pair of longitude boundaries adjusted to fit the data.
    lat_boundaries : List[float]
        The pair of latitude boundaries adjusted to fit the data.
    """

    # Date and geographical limits for the data.
    year_min = min(df[year])
    year_max = max(df[year])
    print(year_min, year_max, min(df[[lon]]))
    # Latitude and Longitude boundaries for the bokeh map
    lon_boundaries = [min(df[lon]) - 15.0,
                      max(df[lon]) + 15.0]

    lon_boundaries = [i * (6378137 * np.pi / 180.0) for i in lon_boundaries]

    lat_boundaries = [min(df[lat]) - 15.0,
                      max(df[lat]) + 15.0]

    lat_boundaries = [np.log(np.tan((90 + i) * np.pi / 360.0)) * 6378137 for i in lat_boundaries]

    return year_min, year_max, lon_boundaries, lat_boundaries


def get_gulf_stream() -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Creates coordinates for a simple representation of the Gulf Stream

    Returns
    -------

    gulf_stream_lon1: List[float]
        A set of longitudes for the gulf stream.
    gulf_stream_lon2: List[float]
        A set of longitudes for the gulf stream.
    gulf_stream_lat1: List[float]
        A set of latitudes for the gulf stream.
    gulf_stream_lat2: List[float]
        A set of latitudes for the gulf stream.
    """
    gulf_stream_lon1 = [0, -40, -85, -85, -75, -65, -20]
    gulf_stream_lon1 = [i * (6378137 * np.pi / 180.0) for i in gulf_stream_lon1]

    gulf_stream_lon2 = [-20, -40, -75]
    gulf_stream_lon2 = [i * (6378137 * np.pi / 180.0) for i in gulf_stream_lon2]

    gulf_stream_lat1 = [0, 5, 20, 25, 25, 40, 60]
    gulf_stream_lat1 = [np.log(np.tan((90 + i) * np.pi / 360.0)) * 6378137 for i in gulf_stream_lat1]

    gulf_stream_lat2 = [10, 10, 25]
    gulf_stream_lat2 = [np.log(np.tan((90 + i) * np.pi / 360.0)) * 6378137 for i in gulf_stream_lat2]

    return gulf_stream_lon1, gulf_stream_lon2, gulf_stream_lat1, gulf_stream_lat2


def additional_legend(loc: str) -> Div:
    """
    Create an additional legend layer for the maps.

    Return
    ------

    div : Div
        an HTML-markup wrapped into a Div bokeh object
    """

    text = """
    The -1 option in number of hurricanes displays every hurricane under the chosen filters.
    
    You can also consult the {} app <a href="http://127.0.0.1:8000/{}">here</a>.
    """.format(loc, loc)
    div = Div(text=text, width=200, height=100)

    return div
