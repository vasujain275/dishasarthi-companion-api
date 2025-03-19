from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
from app.models.rssi_value import RSSIValue
from app.schemas.rssi_value import RSSIValueCreate, RSSIValueUpdate


class RSSIValueRepository:
    def __init__(self, session):
        self.session = session

    async def create_rssi_value(
        self, sample_id: int, rssi_data: RSSIValueCreate
    ) -> RSSIValue:
        new_rssi = RSSIValue(sample_id=sample_id, **rssi_data.model_dump())
        self.session.add(new_rssi)
        await self.session.commit()
        await self.session.refresh(new_rssi)
        return new_rssi

    async def get_rssi_values(self, sample_id: int) -> list[RSSIValue]:
        result = await self.session.execute(
            select(RSSIValue).where(RSSIValue.sample_id == sample_id)
        )
        return result.scalars().all()

    async def get_rssi_value(self, sample_id: int, bssid: str) -> RSSIValue:
        result = await self.session.execute(
            select(RSSIValue).where(
                RSSIValue.sample_id == sample_id, RSSIValue.bssid == bssid
            )
        )
        rssi_value = result.scalar_one_or_none()
        if not rssi_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="RSSI value not found"
            )
        return rssi_value

    async def update_rssi_value(
        self, sample_id: int, bssid: str, rssi_data: RSSIValueUpdate
    ) -> RSSIValue:
        result = await self.session.execute(
            update(RSSIValue)
            .where(RSSIValue.sample_id == sample_id, RSSIValue.bssid == bssid)
            .values(**rssi_data.model_dump(exclude_unset=True))
            .returning(RSSIValue)
        )
        updated = result.scalar_one_or_none()
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="RSSI value not found"
            )
        await self.session.commit()
        return updated

    async def delete_rssi_value(self, sample_id: int, bssid: str) -> None:
        result = await self.session.execute(
            delete(RSSIValue)
            .where(RSSIValue.sample_id == sample_id, RSSIValue.bssid == bssid)
            .returning(RSSIValue.bssid)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="RSSI value not found"
            )
        await self.session.commit()
