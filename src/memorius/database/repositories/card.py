from datetime import datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.models import Card


class CardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_card(
        self,
        deck_id: int,
        question: str,
        answer: str,
        card_type: str = "text",
        variant_1: str | None = None,
        variant_2: str | None = None,
        variant_3: str | None = None,
        variant_4: str | None = None,
        correct_variant: int | None = None,
    ) -> Card:
        """Create new card"""
        card = Card(
            deck_id=deck_id,
            question=question,
            answer=answer,
            card_type=card_type,
            variant_1=variant_1,
            variant_2=variant_2,
            variant_3=variant_3,
            variant_4=variant_4,
            correct_variant=correct_variant,
        )
        self.session.add(card)
        await self.session.commit()
        await self.session.refresh(card)
        return card

    async def get_deck_cards(self, deck_id: int) -> list[Card]:
        """Get all cards in deck"""
        result = await self.session.execute(
            select(Card).where(Card.deck_id == deck_id).order_by(Card.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_cards_for_review(self, deck_id: int) -> list[Card]:
        """Get cards that need review"""
        now = datetime.now()
        result = await self.session.execute(
            select(Card).where(and_(Card.deck_id == deck_id, Card.next_review <= now)).order_by(Card.next_review)
        )
        return list(result.scalars().all())

    async def get_card_by_id(self, card_id: int) -> Card | None:
        """Get card by ID"""
        result = await self.session.execute(select(Card).where(Card.id == card_id))
        return result.scalar_one_or_none()

    async def update_card(
        self,
        card_id: int,
        question: str,
        answer: str,
        card_type: str = "text",
        variant_1: str | None = None,
        variant_2: str | None = None,
        variant_3: str | None = None,
        variant_4: str | None = None,
        correct_variant: int | None = None,
    ) -> None:
        """Update card content"""
        result = await self.session.execute(select(Card).where(Card.id == card_id))
        card = result.scalar_one_or_none()
        if card:
            card.question = question
            card.answer = answer
            card.card_type = card_type
            card.variant_1 = variant_1
            card.variant_2 = variant_2
            card.variant_3 = variant_3
            card.variant_4 = variant_4
            card.correct_variant = correct_variant
            await self.session.commit()

    async def update_card_review(self, card_id: int, difficulty: str) -> None:
        """Update card review statistics using SM-2 algorithm"""
        result = await self.session.execute(select(Card).where(Card.id == card_id))
        card = result.scalar_one_or_none()

        if not card:
            return

        # SM-2 algorithm implementation
        if difficulty == "easy":
            quality = 5
        elif difficulty == "medium":
            quality = 3
        elif difficulty == "hard":
            quality = 2
        else:  # skipped
            quality = 0

        if quality >= 3:
            if card.repetitions == 0:
                card.interval = 1
            elif card.repetitions == 1:
                card.interval = 6
            else:
                card.interval = int(card.interval * card.ease_factor)

            card.repetitions += 1
            card.ease_factor = max(1.3, card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        else:
            card.repetitions = 0
            card.interval = 0

        card.next_review = datetime.now() + timedelta(days=card.interval)
        await self.session.commit()

    async def delete_card(self, card_id: int) -> None:
        """Delete card"""
        result = await self.session.execute(select(Card).where(Card.id == card_id))
        card = result.scalar_one_or_none()
        if card:
            await self.session.delete(card)
            await self.session.commit()
