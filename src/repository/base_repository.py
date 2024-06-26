from datetime import datetime

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_todays_races(self, date: str):
        result = await self.session.execute(
            text("SELECT * from public.select_race_date_race_times(:date)"),
            {"date": datetime.strptime(date, "%Y-%m-%d").date()},
        )
        return pd.DataFrame(result.fetchall())

    async def get_race_by_id(self, date: str, race_id: int):
        result = await self.session.execute(
            text("SELECT * from public.select_form_data_by_race_id(:date, :race_id)"),
            {"date": datetime.strptime(date, "%Y-%m-%d").date(), "race_id": race_id},
        )
        return pd.DataFrame(result.fetchall())

    async def get_race_graph_by_id(self, date: str, race_id: int):
        result = await self.session.execute(
            text(
                "SELECT * from public.select_graph_form_data_by_race_id(:date, :race_id)"
            ),
            {"date": datetime.strptime(date, "%Y-%m-%d").date(), "race_id": race_id},
        )
        return pd.DataFrame(result.fetchall())
