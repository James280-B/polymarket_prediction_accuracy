import os
import pandas as pd


class CSVHandler(object):
    def __init__(self):
        self._pardir = os.path.join(os.path.dirname(__file__), os.pardir)

    def get_file_path(self, filename: str, folder: str) -> str:
        par_dir = self._pardir

        if ".csv" not in filename:
            filename = f"{filename}.csv"

        file_path = os.path.join(par_dir, folder, filename)
        return file_path

    def save_df_to_csv(self, df: pd.DataFrame) -> None:
        file_path = self.get_file_path(filename="tags_list.csv", folder="data")
        df.to_csv(file_path, index=False)

    def get_tags_df(self) -> pd.DataFrame:
        file_path = self.get_file_path(filename="tags_list.csv", folder="data")
        df = pd.read_csv(file_path)
        return df

    def check_file_exists(self, filename: str) -> bool:
        file_path = self.get_file_path(filename=filename, folder="data")
        return os.path.exists(file_path)