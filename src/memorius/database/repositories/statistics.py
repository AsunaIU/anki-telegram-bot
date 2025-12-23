from datetime import datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.models import Statistics


class StatisticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_statistics(self, user_id: int, deck_id: int, card_id: int, difficulty: str) -> None:
        """Add statistics entry"""
        stat = Statistics(
            user_id=user_id,
            deck_id=deck_id,
            card_id=card_id,
            difficulty=difficulty,
        )
        self.session.add(stat)
        await self.session.commit()

    async def get_user_statistics(self, user_id: int, days: int = 30) -> dict:
        """Get user statistics for specified period"""
        start_date = datetime.now() - timedelta(days=days)

        result = await self.session.execute(
            select(Statistics).where(and_(Statistics.user_id == user_id, Statistics.session_date >= start_date))
        )
        stats = result.scalars().all()

        total = len(stats)
        easy = sum(1 for s in stats if s.difficulty == "easy")
        medium = sum(1 for s in stats if s.difficulty == "medium")
        hard = sum(1 for s in stats if s.difficulty == "hard")
        skipped = sum(1 for s in stats if s.difficulty == "skipped")

        return {
            "total": total,
            "easy": easy,
            "medium": medium,
            "hard": hard,
            "skipped": skipped,
            "period_days": days,
        }
