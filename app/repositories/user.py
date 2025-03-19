from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        new_user = User(**user_data.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def get_users(self) -> list[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def get_user(self, user_id: int) -> User:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**user_data.model_dump(exclude_unset=True))
            .returning(User)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self.session.commit()
        return user

    async def delete_user(self, user_id: int) -> None:
        result = await self.session.execute(
            delete(User).where(User.id == user_id).returning(User.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self.session.commit()

    async def get_user_by_username(self, username: str) -> User:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
