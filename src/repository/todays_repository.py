from datetime import datetime

import pandas as pd
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..helpers.session_manager import get_current_session
from .base_repository import BaseRepository


class TodaysRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_todays_races(self):
        result = await self.session.execute(
            text("SELECT * from public.select_race_date_race_times(:date)"),
            {"date": datetime.now().date()},
        )
        return pd.DataFrame(result.fetchall())

    async def get_todays_betfair_ids(self):
        result = await self.session.execute(
            text(
                """
            SELECT 
                id as horse_id, 
                name as horse_name, 
                bf_id as todays_bf_unique_id 
            FROM public.bf_horse
            """
            )
        )
        return pd.DataFrame(result.fetchall())


def get_todays_repository(session: AsyncSession = Depends(get_current_session)):
    return TodaysRepository(session)
