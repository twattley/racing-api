from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import Depends

from ..models.betting_selections import BettingSelections
from ..helpers.session_manager import get_current_session


class BettingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def store_betting_selections(self, selections: BettingSelections) -> dict:
        # change racedate to date type
        race_date = datetime.strptime(selections.race_date, "%Y-%m-%d").date()
        created_at = datetime.now()
        race_id = selections.race_id
        for selection in selections.selections:
            horse_id = selection.horse_id
            betting_type = selection.bet_type

            await self.session.execute(
                text(
                    "INSERT INTO betting.selections (race_date, race_id, horse_id, betting_type, created_at) VALUES (:race_date, :race_id, :horse_id, :betting_type, :created_at)"
                ),
                {
                    "race_date": race_date,
                    "race_id": race_id,
                    "horse_id": horse_id,
                    "betting_type": betting_type,
                    "created_at": created_at,
                },
            )
        await self.session.commit()
        await self.session.execute(text("CALL betting.update_selections_info()"))
        await self.session.commit()
        return {
            "message": f"Stored {len(selections.selections)} selections for race {selections.race_id}"
        }


def get_betting_repository(session: AsyncSession = Depends(get_current_session)):
    return BettingRepository(session)
