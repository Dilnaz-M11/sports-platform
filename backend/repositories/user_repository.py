from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_login(self, login: str) -> User | None:
        result = await self.session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: int, update_data: dict) -> User | None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(**update_data)
        )
        await self.session.commit()
        return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: int) -> bool:
        result = await self.session.execute(
            delete(User).where(User.id == user_id)
        )
        await self.session.commit()
        return result.rowcount > 0