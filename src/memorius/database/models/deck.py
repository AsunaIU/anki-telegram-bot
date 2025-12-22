from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from memorius.database.models.base import Base


class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="decks")  # noqa: F821
    cards: Mapped[list["Card"]] = relationship(  # noqa: F821
        "Card", back_populates="deck", cascade="all, delete-orphan"
    )
