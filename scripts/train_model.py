import os
import sys
import logging
import argparse
import pandas as pd
from whereami.learn import learn

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define the paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TRAINED_DIR = os.path.join(BASE_DIR, "trained")


def train_place_model(place_id):
    """
    Train a whereami model using the exported CSV data for a specific place.

    Args:
        place_id (int): The ID of the place to train a model for

    Returns:
        bool: True if training was successful, False otherwise
    """
    try:
        # Ensure trained directory exists
        place_model_dir = os.path.join(TRAINED_DIR, str(place_id))
        os.makedirs(place_model_dir, exist_ok=True)

        # Find the CSV file for this place_id
        place_csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")]

        if not place_csv_files:
            logger.error(f"No CSV files found in {OUTPUT_DIR}")
            return False

        # For now, take the first CSV file found (in a real system, you'd match the place_id)
        csv_file = os.path.join(OUTPUT_DIR, place_csv_files[0])

        # Use whereami's training function
        # This will read the CSV, train the model, and save it to the specified path
        learn(csv_file=csv_file, model_path=place_model_dir)

        logger.info(f"Successfully trained model for place ID {place_id}")
        return True

    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train whereami models for WiFi fingerprinting"
    )
    parser.add_argument(
        "place_id", type=int, help="The ID of the place to train a model for"
    )

    args = parser.parse_args()

    # Ensure necessary directories exist
    os.makedirs(TRAINED_DIR, exist_ok=True)

    # Train the model
    success = train_place_model(args.place_id)

    if success:
        logger.info(f"Model training completed for place ID {args.place_id}")
        sys.exit(0)
    else:
        logger.error(f"Model training failed for place ID {args.place_id}")
        sys.exit(1)
