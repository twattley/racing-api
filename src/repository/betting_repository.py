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
        race_id = selections.race_id
        for selection in selections.selections:
            horse_id = selection.horse_id
            betting_type = selection.bet_type

            await self.session.execute(
                text(
                    "INSERT INTO betting.selections (race_date, race_id, horse_id, betting_type) VALUES (:race_date, :race_id, :horse_id, :betting_type)"
                ),
                {
                    "race_date": race_date,
                    "race_id": race_id,
                    "horse_id": horse_id,
                    "betting_type": betting_type,
                },
            )
        await self.session.commit()  # Don't forget to commit the transaction
        return {
            "message": f"Stored {len(selections.selections)} selections for race {selections.race_id}"
        }


def get_betting_repository(session: AsyncSession = Depends(get_current_session)):
    return BettingRepository(session)


"""SELECT * FROM betting.selections bs
LEFT JOIN public.unioned_performance_data pd 
on pd.race_id = bs.race_id 
and pd.horse_id = bs.horse_id
and pd.race_date = bs.race_date
"""
