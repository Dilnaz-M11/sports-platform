from sqlalchemy.orm import Session  # ← Изменено: вместо AsyncSession
from sqlalchemy import select, update, delete
from models.user import User

class UserRepository:
    def __init__(self, session: Session):  # ← Изменено: Session вместо AsyncSession
        self.session = session
    
    def create_user(self, user_data: dict) -> User:  # ← убрали async
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int) -> User | None:  # ← убрали async
        result = self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    def get_user_by_login(self, login: str) -> User | None:  # ← убрали async
        result = self.session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()
    
    def get_user_by_email(self, email: str) -> User | None:  # ← убрали async
        result = self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    def update_user(self, user_id: int, update_data: dict) -> User | None:  # ← убрали async
        self.session.execute(
            update(User).where(User.id == user_id).values(**update_data)
        )
        self.session.commit()
        return self.get_user_by_id(user_id)
    
    def delete_user(self, user_id: int) -> bool:  # ← убрали async
        result = self.session.execute(
            delete(User).where(User.id == user_id)
        )
        self.session.commit()
        return result.rowcount > 0