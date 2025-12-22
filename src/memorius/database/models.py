from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    decks: Mapped[list["Deck"]] = relationship("Deck", back_populates="user", cascade="all, delete-orphan")
    statistics: Mapped[list["Statistics"]] = relationship(
        "Statistics", back_populates="user", cascade="all, delete-orphan"
    )


class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="decks")
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="deck", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval: Mapped[int] = mapped_column(Integer, default=0)  # days
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards")


class Statistics(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)  # easy, medium, hard, skipped
    session_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="statistics")
