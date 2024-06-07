from src.helpers.sql_db import create_sync_engine
from src.utils.json_utils import write_json
from src.config import config
import pandas as pd

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
        market_ids['race_time'] = market_ids['race_time'].apply(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S'))
        if market_ids.empty:
            raise ValueError('No market ids found for today')
        write_json(
            market_ids.to_dict('records'), "./src/cache/market_ids.json")
