from sqlalchemy import select, update
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

    async def update_language(self, user_id: int, language_code: str) -> None:
        """Update user's language preference"""
        stmt = update(User).where(User.id == user_id).values(language_code=language_code)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_user_language(self, user_id: int) -> str:
        """Get user's language preference"""
        stmt = select(User.language_code).where(User.id == user_id)
        result = await self.session.execute(stmt)
        language_code = result.scalar_one_or_none()
        return language_code or "en"
