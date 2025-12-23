from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from memorius.database.models.base import Base


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    card_type: Mapped[str] = mapped_column(String(20), default="text", nullable=False)  # 'text' or 'variants'
    variant_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    variant_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    variant_3: Mapped[str | None] = mapped_column(Text, nullable=True)
    variant_4: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_variant: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-4

    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval: Mapped[int] = mapped_column(Integer, default=0)  # days
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards")  # noqa: F821
