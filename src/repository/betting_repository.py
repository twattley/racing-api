from datetime import datetime

import pandas as pd
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..helpers.session_manager import get_current_session
from ..models.betting_selections import BettingSelections


class BettingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def store_betting_selections(
        self, selections: BettingSelections, session_id: int
    ) -> dict:
        race_date = datetime.strptime(selections.race_date, "%Y-%m-%d").date()
        await self.session.execute(text("TRUNCATE TABLE betting.selections"))
        race_id = selections.race_id
        for selection in selections.selections:
            horse_id = selection.horse_id
            betting_type = selection.bet_type
            await self.session.execute(
                text(
                    """
                    INSERT INTO betting.selections (race_date, race_id, horse_id, betting_type, session_id, created_at) 
                    VALUES (:race_date, :race_id, :horse_id, :betting_type, :session_id, :created_at)
                    """
                ),
                {
                    "race_date": race_date,
                    "race_id": race_id,
                    "horse_id": horse_id,
                    "betting_type": betting_type,
                    "session_id": session_id,
                    "created_at": datetime.now(),
                },
            )
        await self.session.commit()
        await self.session.execute(text("CALL betting.update_selections_info()"))
        await self.session.commit()
        return {
            "message": f"Stored {len(selections.selections)} selections for race {selections.race_id}"
        }

    async def get_betting_selections_analysis(self):
        result = await self.session.execute(
            text("SELECT * FROM betting.selections_info")
        )
        return pd.DataFrame(result.fetchall())


def get_betting_repository(session: AsyncSession = Depends(get_current_session)):
    return BettingRepository(session)
