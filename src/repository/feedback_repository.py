import asyncio
from datetime import datetime

import pandas as pd
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..helpers.session_manager import get_current_session


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_todays_races(self):
        result = await self.session.execute(
            text(
                """
                SELECT DISTINCT ON (course, race_time) *
                FROM  public.feedback_performance_data_mat_vw
                WHERE data_type = 'today'
                ORDER BY course, race_time
                """
            ),
        )
        data = pd.DataFrame(result.fetchall())
        return data

    async def get_race_by_id(self, race_id: int):
        result = await self.session.execute(
            text(
                """
                SELECT * 
                    FROM public.feedback_performance_data_mat_vw 
                    WHERE horse_id IN (
                        SELECT horse_id 
                        FROM public.feedback_performance_data_mat_vw 
                        WHERE race_id = :race_id
                    )
                 """
            ),
            {"race_id": race_id},
        )
        return pd.DataFrame(result.fetchall())

    async def get_race_result_by_id(self, race_id: int):
        result = await self.session.execute(
            text(
                """
                    SELECT * 
                        FROM public.feedback_performance_data_mat_vw 
                        WHERE race_id = :race_id
                 """
            ),
            {"race_id": race_id},
        )
        return pd.DataFrame(result.fetchall())

    async def store_current_date_today(self, date: str):
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        try:
            await asyncio.gather(
                self.session.execute(
                    text("UPDATE public.feedback_date SET today_date = :date"),
                    {"date": date_obj},
                ),
                self.session.execute(
                    text("SELECT public.insert_feedback_data_by_date(:date)"),
                    {"date": date_obj},
                ),
            )
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e from e

    async def get_current_date_today(self):
        result = await self.session.execute(
            text("SELECT * from public.feedback_date"),
        )
        return pd.DataFrame(result.fetchall())


def get_feedback_repository(session: AsyncSession = Depends(get_current_session)):
    return FeedbackRepository(session)
