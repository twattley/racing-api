from datetime import datetime
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from ..helpers.session_manager import get_current_session
from ..repository.base_repository import BaseRepository
from ..helpers.logging_config import logger


class FeedbackRepository(BaseRepository):
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_todays_races(self, date: str):
        result = await self.session.execute(
            text("SELECT * from public.select_race_date_race_times(:date)"),
            {'date': datetime.strptime(date, "%Y-%m-%d").date()}
        )
        return pd.DataFrame(result.fetchall())
    
    async def get_race_by_id(self, date: str, race_id: int):
        result = await self.session.execute(
            text("SELECT * from public.select_form_data_by_race_id(:date, :race_id)"),
            {'date': datetime.strptime(date, "%Y-%m-%d").date(), 'race_id': race_id}
        )
        return pd.DataFrame(result.fetchall())

    async def get_race_result_by_id(self, date: str, race_id: int):
        result = await self.session.execute(
            text("SELECT * from public.select_results_data_by_race_id(:date, :race_id)"),
            {'date': datetime.strptime(date, "%Y-%m-%d").date(), 'race_id': race_id}
        )
        return pd.DataFrame(result.fetchall())

def get_feedback_repository(session: AsyncSession = Depends(get_current_session)):
    return FeedbackRepository(session)



