from tools.extraction_tools import extraction_pipeline
from tools.cleaning_tools import cleaning_pipeline
from tools.features_engineering_tools import wgs84_to_web_mercator, zones, season
import pandas as pd
from workflow.df_for_figures import create_start_end_df, create_full_tracks_df


if __name__ == '__main__':

    files_dir = '../files/'

    extraction_pipeline(files_dir=files_dir)

    cleaning_pipeline(files_dir=files_dir)

    file_name = 'df_tracks_after_1970.csv'

    file_path = files_dir + file_name

    df = pd.read_csv(file_path, index_col=0, dtype={'Hour': str}, parse_dates=['Time'])

    print(df.info())

    df = wgs84_to_web_mercator(df=df)

    df = season(df=df)

    df = zones(df=df)

    file_name = 'df_tracks_augmented.csv'

    file_path = files_dir + file_name

    df.to_csv(file_path)

    create_full_tracks_df(file_path=file_path)

    file_name = 'df_full_tracks_bokeh.csv'

    file_path = files_dir + file_name

    create_start_end_df(file_path=file_path)
