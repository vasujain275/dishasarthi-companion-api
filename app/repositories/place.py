from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
from app.models.place import Place
from app.schemas.place import PlaceCreate, PlaceUpdate


class PlaceRepository:
    def __init__(self, session):
        self.session = session

    async def create_place(self, place_data: PlaceCreate) -> Place:
        new_place = Place(**place_data.model_dump())
        self.session.add(new_place)
        await self.session.commit()
        await self.session.refresh(new_place)
        return new_place

    async def get_places(self, user_id: int) -> list[Place]:
        result = await self.session.execute(
            select(Place).where(Place.user_id == user_id)
        )
        return result.scalars().all()

    async def get_place(self, place_id: int) -> Place:
        result = await self.session.execute(select(Place).where(Place.id == place_id))
        place = result.scalar_one_or_none()
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Place not found"
            )
        return place

    async def update_place(self, place_id: int, place_data: PlaceUpdate) -> Place:
        result = await self.session.execute(
            update(Place)
            .where(Place.id == place_id)
            .values(**place_data.model_dump(exclude_unset=True))
            .returning(Place)
        )
        place = result.scalar_one_or_none()
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Place not found"
            )
        await self.session.commit()
        return place

    async def delete_place(self, place_id: int) -> None:
        result = await self.session.execute(
            delete(Place).where(Place.id == place_id).returning(Place.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Place not found"
            )
        await self.session.commit()

    async def get_place_by_name(self, user_id: int, name: str) -> Place:
        result = await self.session.execute(
            select(Place).where(Place.user_id == user_id).where(Place.name == name)
        )
        return result.scalar_one_or_none()
