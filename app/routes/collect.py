from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.collect import CollectData
from app.schemas.user import UserCreate
from app.schemas.place import PlaceCreate
from app.schemas.location import LocationCreate
from app.schemas.sample import SampleCreate
from app.schemas.rssi_value import RSSIValueCreate
from app.repositories.user import UserRepository
from app.repositories.place import PlaceRepository
from app.repositories.location import LocationRepository
from app.repositories.sample import SampleRepository

router = APIRouter(prefix="/collect", tags=["data-collection"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def collect_data(data: CollectData, db: AsyncSession = Depends(get_db)):
    try:
        # Get or create user
        user_repo = UserRepository(db)
        user = await user_repo.get_user_by_username(data.username)
        if not user:
            user = await user_repo.create_user(
                UserCreate(username=data.username)  # Proper schema usage
            )

        # Get or create place
        place_repo = PlaceRepository(db)
        place = await place_repo.get_place_by_name(user.id, data.place)  # Using int ID
        if not place:
            place = await place_repo.create_place(
                PlaceCreate(name=data.place, user_id=user.id)  # int from User model
            )

        # Get or create location
        location_repo = LocationRepository(db)
        location = await location_repo.get_location_by_name(
            place.id, data.location
        )  # int ID
        if not location:
            location = await location_repo.create_location(
                LocationCreate(
                    name=data.location, place_id=place.id  # int from Place model
                )
            )

        # Create samples with RSSI values
        sample_repo = SampleRepository(db)
        for sample in data.samples:
            # Convert RSSI dict to list of RSSIValueCreate
            rssi_values = [
                RSSIValueCreate(bssid=bssid, rssi=rssi)
                for bssid, rssi in sample.rssi_values.items()
            ]

            # Create sample with timestamp
            await sample_repo.create_sample(
                SampleCreate(
                    location_id=location.id,
                    timestamp=sample.timestamp,
                    rssi_values=rssi_values,
                )
            )

        await db.commit()
        return {
            "message": "Data collected successfully",
            "details": {
                "user_id": user.id,
                "place_id": place.id,
                "location_id": location.id,
                "samples_collected": len(data.samples),
            },
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data collection failed: {str(e)}",
        )
