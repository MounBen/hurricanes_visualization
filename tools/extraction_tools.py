import pandas as pd
import numpy as np
from typing import Tuple, List


def load_hurdat(filepath: str) -> Tuple[List[str], List[str]]:
    """
    Extracts hurricane data from hurdat2.txt file

    Parameters
    ----------

    filepath : The pathname to the hurdat2.txt file


    Return
    ------

    tracks : List[str]
                Contains all geographical data from hurdat2.txt
    hurricanes : List[str]
                Contains all hurricanes with ID, name and number of corresponding data points
    """

    # Loading the text file:
    tracks = []
    hurricanes = []

    # When reading the text file, we separate two possible line formats: whether the line contains an ID or not. This is
    # due to the fact that ID's are followed by the corresponding data points without anymore mention of the ID.
    # So it will be easier, later on to just add the ID's separately.
    with open(filepath) as text:
        for line in text:

            if line.startswith('AL'):
                hurricanes.append(line)
            else:
                tracks.append(line)

    print(hurricanes[:5])
    print('\n')
    print(tracks[:15])
    print('\n')
    print('There are {} different hurricanes, for a total of {} measurements.'
          .format(len(hurricanes), len(tracks)))
    print('\n')

    return tracks, hurricanes


def create_hurricanes_df(hurricanes_list: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """
    Transforms hurricane_list into a pandas DataFrame

    Parameters
    ----------

    hurricanes_list: List[str]
            Contains, for each hurricane its' ID, name and number of associated data points

    Return
    ------
    df_temp: pd.DataFrame
            A DataFrame containing the same information as hurricanes, nicely packed.
    id_list: List[str]
            A list containing the ID's repeated for each observation
    """

    # Creation of the DataFrame.

    df_temp = pd.DataFrame(hurricanes_list)
    df_temp = df_temp.iloc[:, 0].str.split(",", expand=True)

    # The fourth column just contains the \n characters so we can drop it.
    df_temp.drop(columns=[3], inplace=True)

    df_temp.columns = ['ID', 'Name', 'Data_length']

    df_temp.ID = df_temp.ID.astype('str')
    df_temp.Name = df_temp.Name.astype('str')
    df_temp.Data_length = df_temp.Data_length.astype('int64')

    # Extraction of the Year from the ID
    df_temp['Year'] = df_temp.ID.map(lambda x: x[-4:])
    df_temp.Year = df_temp.Year.astype('int64')

    id_list = []

    for i in range(df_temp.index.size):
        id_list = id_list + [df_temp.iloc[i, 0]] * df_temp.iloc[i, 2]

    return df_temp, id_list


def create_tracks_df(tracks_list: List[str], id_list: List[str]) -> pd.DataFrame:
    """
    Transforms tracks_list into a pandas DataFrame

    Parameters
    ----------

    tracks_list: List[str]
            Contains all geographical data from hurdat2.txt
    id_list: List[str]
            Contains the ID's repeated for each data point

    Return
    ------
    df_temp: pd.DataFrame
            A DataFrame containing the full track of each hurricane.
    """

    df_temp = pd.DataFrame(tracks_list)
    df_temp = df_temp.iloc[:, 0].str.split(",", expand=True)

    # Names of the columns obtained from 'tracks-hurdat2-epac-format-feb16.pdf'
    cols = ['Date', 'Hour', 'Events', 'Status', 'Latitude', 'Longitude',
            'Max_Speed', 'Min_Pressure', 'Low_Rad_NE', 'Low_Rad_SE',
            'Low_Rad_SW', 'Low_Rad_NW', 'Med_Rad_NE', 'Med_Rad_SE',
            'Med_Rad_SW', 'Med_Rad_NW', 'High_Rad_NE', 'High_Rad_SE',
            'High_Rad_SW', 'High_Rad_NW', 'extra_char']

    df_temp.columns = cols

    # Unnecessary columns for tracks visualization, last columns contains only '\n'.
    df_temp.drop(columns=['extra_char', 'Events'], inplace=True)

    df_temp.insert(loc=0, value=pd.Series(id_list), column='ID')

    # Change most columns to floats.
    for col in cols[6:-1]:
        df_temp[col] = df_temp[col].astype('float64')

    # Replace -999 by NaN's for better visibility (chosen format in hurdat2.txt)
    df_temp = df_temp.replace(to_replace=-999, value=np.nan)

    # Max_speed column may '-99' values, we assume it's a typo for -999, which is a missing value.
    if df_temp.loc[df_temp.Max_Speed < 0].Max_Speed.value_counts().values > 0:
        df_temp.replace(to_replace={'Max_Speed': {-99:np.nan}}, inplace=True)
        print('There were missing values in the Max_Speed column.')
        print('\n')

    print(df_temp.columns)
    print('\n')

    return df_temp


def extraction_pipeline(files_dir: str, hurdat_name: str = 'hurdat2.txt',
                        name_1: str = 'df_names', name_2:str = 'df_tracks'):
    """
    Extracts and saves as csv files two DataFrame 'df_names' and 'df_tracks' from the NOAA text data.

    df_names contains the ID, names, and length of every hurricane.
    df_tracks contains all the data points for every hurricane.

    Parameters
    ----------

    files_dir: str
            Path to the directory which contains the NOAA text data.
    hurdat_name: str
            Name of the file containing the NOAA text data.
    name_1: str
            Name to use for saving the ID DataFrame
    name_2: str
            Name to use for saving the tracks DataFrame

    Return
    ------

    """
    hurdat_path = files_dir + hurdat_name

    tracks, hurricanes = load_hurdat(filepath=hurdat_path)

    df_names, id_list = create_hurricanes_df(hurricanes_list=hurricanes)

    save_names = files_dir + name_1 + '.csv'
    df_names.to_csv(save_names)

    df_tracks = create_tracks_df(tracks_list=tracks, id_list=id_list)

    save_tracks = files_dir + name_2 + '.csv'
    df_tracks.to_csv(save_tracks)

    print(df_tracks.info())
    print('\n')
    print('There are {} missing values in the tracks DataFrame, most of which are located in the radii columns.'
          .format(df_tracks.isnull().sum().sum()))
    print('\n')
    print(df_tracks.head(2))

