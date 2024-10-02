import pandas as pd
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..helpers.session_manager import get_current_session


class TodaysRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_todays_races(self):
        result = await self.session.execute(
            text(
                """
                SELECT DISTINCT ON (course, race_time) *
                FROM  public.todays_performance_data_mat_vw
                WHERE data_type = 'today'
                ORDER BY course, race_time
                """
            ),
        )
        return pd.DataFrame(result.fetchall())

    async def get_race_by_id(self, race_id: int):
        result = await self.session.execute(
            text(
                """
                SELECT pd.*, h.bf_id::integer as betfair_id
                    FROM public.todays_performance_data_mat_vw pd
					LEFT JOIN public.horse h
					on h.id = pd.horse_id
                    WHERE horse_id IN (
                        SELECT pd.horse_id 
                        FROM public.todays_performance_data_mat_vw pd
                        WHERE pd.race_id = :race_id
                    )
                 """
            ),
            {"race_id": race_id},
        )
        return pd.DataFrame(result.fetchall())


def get_todays_repository(session: AsyncSession = Depends(get_current_session)):
    return TodaysRepository(session)
