# app/routes/predict.py
import os
import json
import logging
from typing import Dict, List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.place import Place
from whereami.predict import predict_proba

# Define the directory where trained models are stored
TRAINED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "trained"
)

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.websocket("/{place_id}")
async def predict_location(
    websocket: WebSocket, place_id: int, db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time location prediction.

    1. Client connects to this endpoint
    2. Client sends RSSI data in the format: {"rssi_values": {"BSSID1": RSSI1, "BSSID2": RSSI2, ...}}
    3. Server responds with the predicted location name
    4. Connection remains open until client disconnects
    """
    try:
        # Check if place exists
        place_result = await db.execute(select(Place).where(Place.id == place_id))
        place = place_result.scalar_one_or_none()

        if not place:
            # Can't use HTTPException in websocket connections, so we'll close with an error code
            await websocket.close(
                code=4004, reason=f"Place with ID {place_id} not found"
            )
            return

        # Check if trained model exists for this place
        model_dir = os.path.join(TRAINED_DIR, str(place_id))
        if not os.path.exists(model_dir):
            await websocket.close(
                code=4004, reason=f"No trained model found for place ID {place_id}"
            )
            return

        # Accept the connection
        await websocket.accept()

        # Send initial message
        await websocket.send_text(
            json.dumps(
                {
                    "status": "connected",
                    "message": f"Connected to prediction service for {place.name}",
                    "place_id": place_id,
                }
            )
        )

        # Main loop for receiving and processing messages
        while True:
            # Wait for RSSI data from client
            data = await websocket.receive_text()

            try:
                # Parse the received data
                rssi_data = json.loads(data)

                # Validate the format
                if not isinstance(rssi_data, dict) or "rssi_values" not in rssi_data:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "error": "Invalid data format. Expected {'rssi_values': {BSSID: RSSI, ...}}"
                            }
                        )
                    )
                    continue

                # Extract RSSI values
                rssi_values = rssi_data["rssi_values"]
                if not isinstance(rssi_values, dict):
                    await websocket.send_text(
                        json.dumps(
                            {
                                "error": "Invalid RSSI values format. Expected {BSSID: RSSI, ...}"
                            }
                        )
                    )
                    continue

                # Use whereami to predict location
                # The predict_proba function expects a dictionary with BSSID keys and RSSI values
                prediction_result = predict_proba(rssi_values, model_path=model_dir)

                # Extract the most likely location and its probability
                if prediction_result and len(prediction_result) > 0:
                    # prediction_result is a list of (location, probability) tuples
                    # Sort by probability (descending) and take the top result
                    prediction_result.sort(key=lambda x: x[1], reverse=True)
                    top_location, confidence = prediction_result[0]

                    # Send prediction to client
                    await websocket.send_text(
                        json.dumps(
                            {
                                "prediction": top_location,
                                "confidence": confidence,
                                "all_predictions": [
                                    {"location": loc, "confidence": conf}
                                    for loc, conf in prediction_result
                                ],
                            }
                        )
                    )
                else:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "error": "Could not make a prediction",
                                "prediction": None,
                                "confidence": 0.0,
                            }
                        )
                    )

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
            except Exception as e:
                logging.error(f"Prediction error: {str(e)}")
                await websocket.send_text(
                    json.dumps({"error": f"Prediction failed: {str(e)}"})
                )

    except WebSocketDisconnect:
        logging.info(
            f"Client disconnected from prediction service for place {place_id}"
        )
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.close(code=1011, reason=f"Server error: {str(e)}")
        except:
            pass
