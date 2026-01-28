import pandas as pd
import requests
import datetime as dt

from polymarket_prediction_accuracy.scr.utils.poly_utils import PolyUtilsHandler
from polymarket_prediction_accuracy.scr.data_handler import csv_handler
from polymarket_prediction_accuracy.scr.data_handler.subgraph_data_handler import SubgraphDataHandler
from polymarket_prediction_accuracy.scr.utils import parameters


class PolyDataHandler(object):
    API_KEY = parameters.read_environment_variable("API_KEY")

    _polymarket_tag_list_url = "https://gamma-api.polymarket.com/tags"
    _polymarket_markets_via_id_url = "https://gamma-api.polymarket.com/markets"
    _polymarket_historical_time_series_url = "https://clob.polymarket.com/prices-history"

    _utc_time_tol = dt.timedelta(hours=13)

    def __init__(
            self,
            num_markets: int | str,
            input_labels: list,
            resolution: int,
            horizon: str
    ) -> None:
        self.input_labels = input_labels
        self.num_markets = num_markets
        self.resolution = resolution
        self.horizon = horizon

    def _generate_tag_list(self) -> None:
        resp = requests.get(url=self._polymarket_tag_list_url)
        resp.raise_for_status()

        tag_list = resp.json()
        tag_list_df = pd.DataFrame(tag_list)

        csv = csv_handler.CSVHandler()
        csv.save_df_to_csv(tag_list_df)

        return None

    def _select_user_tags(self) -> pd.DataFrame:
        csv = csv_handler.CSVHandler()
        tags_df = csv.get_tags_df()

        self._check_tag_is_in_list()

        user_tags_df = tags_df[tags_df["label"].isin(self.input_labels)]

        return user_tags_df

    def _check_tag_is_in_list(self) -> None:
        csv = csv_handler.CSVHandler()
        tags_df = csv.get_tags_df()

        if ~tags_df["label"].isin(self.input_labels).any():
            raise Exception(f"Tag '{self.input_labels}' not found.")

    def _request_market_data_via_tag_id(self, tag_id: int) -> pd.DataFrame:
        params = {
            "tag_id": tag_id,
            "limit": self.num_markets,
            "closed": True,
        }

        resp = requests.get(url=self._polymarket_markets_via_id_url, params=params)
        resp.raise_for_status()

        market_data = resp.json()
        market_data_df = pd.DataFrame(market_data)

        return market_data_df

    def _build_full_market_data_df(self, user_tags_df: pd.DataFrame) -> pd.DataFrame:
        full_market_data_df = pd.DataFrame()

        for i in user_tags_df["id"]:
            market_data_df = self._request_market_data_via_tag_id(i)
            full_market_data_df = pd.concat([full_market_data_df, market_data_df], ignore_index=True)

        return full_market_data_df

    def generate_evaluation_times(self, market_end_time: str) -> tuple:
        poly_utils = PolyUtilsHandler()
        market_end_time_utc = poly_utils.cast_poly_to_utc(market_end_time)
        start_time_utc = None
        if self.horizon == "1w":
            start_time_utc = market_end_time_utc - dt.timedelta(days=7)
        elif self.horizon == "1m":
            start_time_utc = market_end_time_utc - dt.timedelta(days=30)

        evaluation_utc = start_time_utc

        return start_time_utc, market_end_time_utc, evaluation_utc

    @staticmethod
    def _find_winning_token_id(market_condition_id: str) -> int | None:
        winning_token_id = None

        sub_graph_data = SubgraphDataHandler(condition_id=market_condition_id)
        subgraph_data_dd = sub_graph_data.output_query_data()

        payout_location = subgraph_data_dd["data"]["condition"]["payoutNumerators"]
        winner_denominator_location = subgraph_data_dd["data"]["condition"]["payoutDenominator"]
        token_id_location = subgraph_data_dd["data"]["condition"]["positionIds"]

        for i in range(len(payout_location)):
            if payout_location[i] == winner_denominator_location:
                winning_token_id = token_id_location[i]

        return winning_token_id

    def _get_clob_data_via_market_id(
            self,
            full_market_data_df: pd.DataFrame,
    ) -> pd.DataFrame:
        full_clob_data_df = pd.DataFrame()

        poly_utils = PolyUtilsHandler()

        for i in range(len(full_market_data_df)):
            market_condition_id = full_market_data_df["conditionId"][i]
            winning_token_id = self._find_winning_token_id(market_condition_id)
            end_date = full_market_data_df["endDate"][i]
            datetime_times = self.generate_evaluation_times(end_date)

            data_start_time_utc = datetime_times[0]
            data_end_time_utc = datetime_times[1]
            evaluation_utc = datetime_times[2]
            params = {
                "market": winning_token_id,
                "endTs": data_end_time_utc.timestamp(),
                "startTs": data_start_time_utc.timestamp(),
                "fidelity": self.resolution,
            }

            resp = requests.get(url=self._polymarket_historical_time_series_url, params=params)
            resp.raise_for_status()
            clob_data = resp.json()
            clob_data_df = pd.DataFrame(data=clob_data)

            clob_data_df["token_id"] = winning_token_id
            clob_data_df["evaluation_time"] = evaluation_utc
            clob_data_df["times"] = clob_data_df["history"].apply(lambda x: x["t"])
            clob_data_df["times"] = clob_data_df["times"].apply(poly_utils.cast_utc_to_datetime)
            clob_data_df["price"] = clob_data_df["history"].apply(lambda x: x["p"])

            full_clob_data_df = pd.concat(
                objs=[full_clob_data_df, clob_data_df],
                ignore_index=True,
            )
            print(f"market {i} data completed")

        cleaned_clob_data_df = full_clob_data_df.drop(columns=["history"])

        print(cleaned_clob_data_df["times"])
        print(cleaned_clob_data_df["evaluation_time"])

        time_filter = abs(cleaned_clob_data_df["times"] - cleaned_clob_data_df["evaluation_time"]) <= self._utc_time_tol
        filtered_clob_data_df = cleaned_clob_data_df[time_filter]

        return filtered_clob_data_df

    def build_data_set(self) -> pd.DataFrame:
        csv = csv_handler.CSVHandler()
        if not csv.check_file_exists(filename="tags_list.csv"):
            self._generate_tag_list()

        user_tags_df = self._select_user_tags()
        full_market_data_df = self._build_full_market_data_df(user_tags_df)
        full_clob_data_df = self._get_clob_data_via_market_id(full_market_data_df)

        return full_clob_data_df
