import os
import csv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.place import Place
from app.models.location import Location
from app.models.sample import Sample
from app.models.rssi_value import RSSIValue
import logging

# Create output directory if it doesn't exist
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

router = APIRouter(prefix="/output", tags=["data-export"])


@router.get("/{place_id}", response_class=FileResponse)
async def export_place_data(place_id: int, db: AsyncSession = Depends(get_db)):
    """
    Export all RSSI data for a specific place to a CSV file format compatible with whereami.
    The file is saved in the output directory as place_name.csv.
    """
    try:
        # Get the place information
        place_result = await db.execute(select(Place).where(Place.id == place_id))
        place = place_result.scalar_one_or_none()

        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Place with ID {place_id} not found",
            )

        # Create CSV filename
        place_name = place.name.replace(" ", "_").lower()
        csv_filename = f"{place_name}.csv"
        csv_path = os.path.join(OUTPUT_DIR, csv_filename)

        # Get all locations for this place
        locations_result = await db.execute(
            select(Location).where(Location.place_id == place_id)
        )
        locations = locations_result.scalars().all()

        if not locations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No locations found for place with ID {place_id}",
            )

        # Dictionary to hold all unique BSSIDs
        all_bssids = set()

        # Dictionary to hold all samples by location
        samples_by_location = {}

        # Collect all data
        for location in locations:
            # Get samples for this location
            samples_result = await db.execute(
                select(Sample).where(Sample.location_id == location.id)
            )
            samples = samples_result.scalars().all()

            if not samples:
                continue

            # Initialize samples for this location
            samples_by_location[location.name] = []

            # Get RSSI values for each sample
            for sample in samples:
                rssi_values_result = await db.execute(
                    select(RSSIValue).where(RSSIValue.sample_id == sample.id)
                )
                rssi_values = rssi_values_result.scalars().all()

                # Convert to dictionary for easier processing
                rssi_dict = {rssi.bssid: rssi.rssi for rssi in rssi_values}

                # Add to all BSSIDs
                all_bssids.update(rssi_dict.keys())

                # Add to samples for this location
                samples_by_location[location.name].append(rssi_dict)

        if not all_bssids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No RSSI data found for place with ID {place_id}",
            )

        # Sort BSSIDs for consistent column order
        sorted_bssids = sorted(list(all_bssids))

        # CSV header: "location" + all BSSIDs
        header = ["location"] + sorted_bssids

        # Open CSV file for writing
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            # Write data for each location and sample
            for location_name, samples in samples_by_location.items():
                for sample in samples:
                    row = [location_name]
                    # Add RSSI value for each BSSID, or -100 if not detected
                    for bssid in sorted_bssids:
                        row.append(sample.get(bssid, -100))
                    writer.writerow(row)

        # Return the CSV file
        return FileResponse(
            path=csv_path,
            filename=csv_filename,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={csv_filename}"},
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error exporting data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}",
        )
