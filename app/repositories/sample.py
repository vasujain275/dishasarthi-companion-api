from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
from app.models.sample import Sample
from app.models.rssi_value import RSSIValue
from app.schemas.sample import SampleCreate, SampleUpdate


class SampleRepository:
    def __init__(self, session):
        self.session = session

    async def create_sample(self, sample_data: SampleCreate) -> Sample:
        # Create Sample with timestamp
        new_sample = Sample(
            location_id=sample_data.location_id,
            timestamp=sample_data.timestamp,  # Add timestamp
        )
        self.session.add(new_sample)
        await self.session.flush()

        # Create RSSI values
        rssi_values = [
            RSSIValue(sample_id=new_sample.id, bssid=rssi.bssid, rssi=rssi.rssi)
            for rssi in sample_data.rssi_values
        ]
        self.session.add_all(rssi_values)

        await self.session.commit()
        await self.session.refresh(new_sample)
        return new_sample

    async def get_samples(self, location_id: int) -> list[Sample]:
        result = await self.session.execute(
            select(Sample).where(Sample.location_id == location_id)
        )
        return result.scalars().all()

    async def get_sample(self, sample_id: int) -> Sample:
        result = await self.session.execute(
            select(Sample).where(Sample.id == sample_id)
        )
        sample = result.scalar_one_or_none()
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found"
            )
        return sample

    async def update_sample(self, sample_id: int, sample_data: SampleUpdate) -> Sample:
        result = await self.session.execute(
            update(Sample)
            .where(Sample.id == sample_id)
            .values(**sample_data.model_dump(exclude_unset=True))
            .returning(Sample)
        )
        sample = result.scalar_one_or_none()
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found"
            )
        await self.session.commit()
        return sample

    async def delete_sample(self, sample_id: int) -> None:
        result = await self.session.execute(
            delete(Sample).where(Sample.id == sample_id).returning(Sample.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found"
            )
        await self.session.commit()
