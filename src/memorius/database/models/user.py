from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from memorius.database.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str] = mapped_column(String(2), default="ru", server_default="ru", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    decks: Mapped[list["Deck"]] = relationship(  # noqa: F821
        "Deck", back_populates="user", cascade="all, delete-orphan"
    )
    statistics: Mapped[list["Statistics"]] = relationship(  # noqa: F821
        "Statistics", back_populates="user", cascade="all, delete-orphan"
    )
