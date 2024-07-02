from datetime import datetime

import pandas as pd
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..helpers.session_manager import get_current_session
from ..repository.base_repository import BaseRepository


class FeedbackRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_race_result_by_id(self, date: str, race_id: int):
        result = await self.session.execute(
            text(
                "SELECT * from public.select_results_data_by_race_id(:date, :race_id)"
            ),
            {"date": datetime.strptime(date, "%Y-%m-%d").date(), "race_id": race_id},
        )
        return pd.DataFrame(result.fetchall())


def get_feedback_repository(session: AsyncSession = Depends(get_current_session)):
    return FeedbackRepository(session)
