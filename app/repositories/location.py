from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate


class LocationRepository:
    def __init__(self, session):
        self.session = session

    async def create_location(self, location_data: LocationCreate) -> Location:
        new_location = Location(**location_data.model_dump())
        self.session.add(new_location)
        await self.session.commit()
        await self.session.refresh(new_location)
        return new_location

    async def get_locations(self, place_id: int) -> list[Location]:
        result = await self.session.execute(
            select(Location).where(Location.place_id == place_id)
        )
        return result.scalars().all()

    async def get_location(self, location_id: int) -> Location:
        result = await self.session.execute(
            select(Location).where(Location.id == location_id)
        )
        location = result.scalar_one_or_none()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )
        return location

    async def update_location(
        self, location_id: int, location_data: LocationUpdate
    ) -> Location:
        result = await self.session.execute(
            update(Location)
            .where(Location.id == location_id)
            .values(**location_data.model_dump(exclude_unset=True))
            .returning(Location)
        )
        location = result.scalar_one_or_none()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )
        await self.session.commit()
        return location

    async def delete_location(self, location_id: int) -> None:
        result = await self.session.execute(
            delete(Location).where(Location.id == location_id).returning(Location.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
            )
        await self.session.commit()

    async def get_location_by_name(self, place_id: int, name: str) -> Location:
        result = await self.session.execute(
            select(Location)
            .where(Location.place_id == place_id)
            .where(Location.name == name)
        )
        return result.scalar_one_or_none()
