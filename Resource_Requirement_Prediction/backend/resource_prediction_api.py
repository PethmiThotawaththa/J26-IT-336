
from functools import lru_cache
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException
from joblib import load
from pydantic import BaseModel, ConfigDict, Field, model_validator


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "outputs" / "demo_resource_model.joblib"

FEATURES = [
    "repair_type",
    "quantity",
    "quantity_unit",
    "priority",
]

TARGETS = [
    "labour_person_days",
    "asphalt_tonnes",
    "aggregate_tonnes",
    "equipment_hours",
]

app = FastAPI(
    title="Road Maintenance Resource Prediction API",
    description=(
        "Research prototype for predicting labour, material, "
        "and equipment requirements for road maintenance tasks."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# Request validation
# --------------------------------------------------

class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
    )

    repair_type: Literal[
        "pothole_patch",
        "drain_cleaning",
        "resurfacing",
    ]

    quantity: float = Field(
        gt=0,
        le=1_000_000,
        description="Maintenance quantity; must be positive.",
    )

    quantity_unit: Literal["sq_m", "metres"] = Field(
        description="sq_m for pothole_patch/resurfacing; metres for drain_cleaning."
    )

    @model_validator(mode="after")
    def validate_quantity_unit(self):
        expected_units = {
            "pothole_patch": "sq_m",
            "drain_cleaning": "metres",
            "resurfacing": "sq_m",
        }
        expected_unit = expected_units[self.repair_type]
        if self.quantity_unit != expected_unit:
            raise ValueError(
                f"{self.repair_type} requires quantity_unit "
                f"'{expected_unit}', not '{self.quantity_unit}'."
            )
        return self

    priority: float = Field(
        ge=0,
        le=10,
        description="Task priority from 0 to 10.",
    )


# --------------------------------------------------
# Model loading
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Trained model not found at: {MODEL_PATH}. "
            "Run python src/train_resource_model.py first."
        )

    return load(MODEL_PATH)


def model_is_available() -> bool:
    return MODEL_PATH.is_file()


# --------------------------------------------------
# API endpoints
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Road Maintenance Resource Prediction API",
        "status": "running",
        "documentation": "/docs",
        "data_status": "SIMULATED",
    }


@app.get("/health")
def health():
    available = model_is_available()

    return {
        "status": "ok" if available else "degraded",
        "model_available": available,
        "data_status": "SIMULATED",
    }


@app.get("/model-info")
def model_info():
    return {
        "model_type": "RandomForestRegressor",
        "input_features": FEATURES,
        "predicted_resources": TARGETS,
        "model_path": str(MODEL_PATH),
        "training_data_status": "SIMULATED",
        "warning": (
            "Predictions have not been validated against "
            "actual RDA resource-consumption records."
        ),
    }


@app.post("/predict")
def predict_resources(request: PredictionRequest):
    # Return a clear service error if the model is unavailable.
    try:
        model = get_model()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="The saved model could not be loaded.",
        ) from exc

    # Construct the input using the exact feature names
    # and ordering used during model training.
    task = pd.DataFrame(
        [
            {
                "repair_type": request.repair_type,
                "quantity": request.quantity,
                "quantity_unit": request.quantity_unit,
                "priority": request.priority,
            }
        ],
        columns=FEATURES,
    )

    try:
        predictions = model.predict(task)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The resource prediction could not be completed.",
        ) from exc

    if len(predictions) != 1 or len(predictions[0]) != len(TARGETS):
        raise HTTPException(
            status_code=500,
            detail="The model returned an unexpected output shape.",
        )

    predicted_resources = {}

    for name, value in zip(TARGETS, predictions[0]):
        number = float(value)

        if not pd.notna(number) or number == float("inf") or number == float("-inf"):
            raise HTTPException(
                status_code=500,
                detail=f"The model returned an invalid value for {name}.",
            )

        # Resource requirements cannot be negative.
        # Clip only the returned estimate; this does not retrain the model.
        predicted_resources[name] = round(max(0.0, number), 3)

    return {
        "input": request.model_dump(),
        "predicted_resources": predicted_resources,
        "data_status": "SIMULATED",
        "warning": (
            "Research prototype only. Validate against approved "
            "engineering norms or actual resource records before use."
        ),
    }
