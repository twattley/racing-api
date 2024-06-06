from datetime import datetime
from fastapi import Depends
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..helpers.session_manager import get_current_session
from .base_repository import BaseRepository


class TodaysRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_todays_races(self):
        result = await self.session.execute(
            text("SELECT * from public.select_race_date_race_times(:date)"),
            {"date": datetime.now().strftime("%Y-%m-%d")},
        )
        return pd.DataFrame(result.fetchall())

    async def get_todays_betfair_ids(self):
        result = await self.session.execute(text("SELECT * FROM public.bf_horse"))
        return pd.DataFrame(result.fetchall())


def get_todays_repository(session: AsyncSession = Depends(get_current_session)):
    return TodaysRepository(session)
