from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from memorius.database.models import Deck


class DeckRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_deck(self, user_id: int, name: str) -> Deck:
        """Create new deck"""
        deck = Deck(user_id=user_id, name=name)
        self.session.add(deck)
        await self.session.commit()
        await self.session.refresh(deck)
        return deck

    async def get_user_decks(self, user_id: int) -> list[Deck]:
        """Get all user decks"""
        result = await self.session.execute(
            select(Deck)
            .where(Deck.user_id == user_id)
            .options(selectinload(Deck.cards))
            .order_by(Deck.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_deck_by_id(self, deck_id: int) -> Deck | None:
        """Get deck by ID"""
        result = await self.session.execute(select(Deck).where(Deck.id == deck_id).options(selectinload(Deck.cards)))
        return result.scalar_one_or_none()

    async def delete_deck(self, deck_id: int) -> None:
        """Delete deck"""
        result = await self.session.execute(select(Deck).where(Deck.id == deck_id))
        deck = result.scalar_one_or_none()
        if deck:
            await self.session.delete(deck)
            await self.session.commit()
