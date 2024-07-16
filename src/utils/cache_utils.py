import pandas as pd

from src.config import config
from src.helpers.sql_db import create_sync_engine
from src.utils.json_utils import write_json

CACHE_DIR = "./src/cache"


def construct_cache_data():
    with create_sync_engine(config).begin() as conn:
        market_ids = pd.read_sql(
            """
            SELECT race_time, race_id, market_id_win, market_id_place 
            FROM public.bf_market
            where race_time::date = current_date
            """,
            con=conn,
        )
        market_ids["race_time"] = market_ids["race_time"].apply(
            lambda x: x.strftime("%Y-%m-%dT%H:%M:%S")
        )
        if market_ids.empty:
            raise ValueError("No market ids found for today")
        write_json(
            market_ids.to_dict("records"),
            f"{CACHE_DIR}/market_ids.json",
        )


def save_todays_prices(data: pd.DataFrame, filepath: str) -> None:
    today = data[data["data_type"] == "today"][
        [
            "horse_name",
            "betfair_win_sp",
            "betfair_place_sp",
            "official_rating",
            "race_id",
            "horse_id",
        ]
    ].astype(
        {
            "horse_name": "str",
            "betfair_win_sp": "float",
            "betfair_place_sp": "float",
            "official_rating": "Int64",
            "race_id": "Int64",
            "horse_id": "Int64",
        }
    )
    write_json(
        today.to_dict("records"),
        filepath,
    )
