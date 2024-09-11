from datetime import datetime

import pandas as pd
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..helpers.session_manager import get_current_session


class CollateralRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_collateral_form_by_id(
        self, race_date: str, race_id: int, todays_race_date: str, horse_id: int
    ):
        result = await self.session.execute(
            text(
                "SELECT * from public.select_collateral_form_data_by_race_id(:race_date, :race_id, :todays_race_date, :horse_id)"
            ),
            {
                "race_date": datetime.strptime(race_date, "%Y-%m-%d").date(),
                "race_id": race_id,
                "todays_race_date": datetime.strptime(
                    todays_race_date, "%Y-%m-%d"
                ).date(),
                "horse_id": horse_id,
            },
        )
        return pd.DataFrame(result.fetchall())


def get_collateral_repository(session: AsyncSession = Depends(get_current_session)):
    return CollateralRepository(session)
