from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from memorius.database.models.base import Base


class Statistics(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)  # easy, medium, hard, skipped
    session_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="statistics")  # noqa: F821
