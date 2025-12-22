from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Get existing user or create new one"""
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

        return user

    async def update_phone(self, user_id: int, phone_number: str) -> None:
        """Update user phone number"""
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.phone_number = phone_number
            await self.session.commit()
