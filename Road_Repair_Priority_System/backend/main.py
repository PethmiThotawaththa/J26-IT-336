
from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# --------------------------------------------------
# Project paths and existing trained models
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

MODEL_FILES = {
    "repair_cost": "final_extra_trees_cost_model.joblib",
    "repair_method": "experimental_pavement_repair_model.joblib",
    "repair_priority": "experimental_priority_classifier.joblib",
}

PRIORITY_FEATURES = [
    "section_length_m",
    "traffic_mean_vehicles_per_hour",
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "section_forecast_budget_lkr",
    "planned_item_1_count",
    "planned_item_2_count",
    "planned_item_75_count",
]

METHOD_FEATURES = [
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
]

COST_FEATURES = [
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Length (m)",
    "Width (m)",
    "Calculated_Work_Area_sqm",
    "Item Code",
    "Units",
]

REPAIR_METHOD_NAMES = {
    1: "Pothole Patching",
    2: "Crack Sealing",
    75: "Section Overlay",
}

# Categories verified from the saved cost model.
VALID_COST_ITEM_CODES = {
    "1", "2", "40", "42", "43", "44", "45", "46",
    "50", "51", "52", "53", "54", "59", "60",
    "61", "62", "63", "64", "66", "67", "69",
    "70", "71", "75",
}

VALID_COST_UNITS = {
    "m",
    "m.ton",
    "no",
    "sq.m",
}


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="RoadWise AI API",
    description="Road Repair Prediction and Decision Support System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Load existing models (read-only)
# --------------------------------------------------

loaded_models = {}
model_status = {}


def load_existing_models():
    for model_name, filename in MODEL_FILES.items():
        model_path = MODELS_DIR / filename

        if not model_path.exists():
            model_status[model_name] = {
                "loaded": False,
                "error": "Model file not found",
            }
            continue

        try:
            saved_object = joblib.load(model_path)

            if isinstance(saved_object, dict):
                model = saved_object.get("model")
            else:
                model = saved_object

            if model is None or not hasattr(model, "predict"):
                raise ValueError(
                    "Saved file does not contain a valid predictor"
                )

            loaded_models[model_name] = model

            model_status[model_name] = {
                "loaded": True,
                "algorithm": type(model).__name__,
                "filename": filename,
            }

        except Exception as error:
            model_status[model_name] = {
                "loaded": False,
                "error": str(error),
            }


load_existing_models()


# --------------------------------------------------
# Request schemas
# --------------------------------------------------

class PriorityPredictionInput(BaseModel):
    section_length_m: float = Field(ge=0, allow_inf_nan=False)

    traffic_mean_vehicles_per_hour: float = Field(
        ge=0,
        allow_inf_nan=False,
    )

    nearby_hospital_count_500m: int = Field(ge=0)
    nearby_school_count_500m: int = Field(ge=0)
    nearby_police_count_500m: int = Field(ge=0)

    section_forecast_budget_lkr: float = Field(
        ge=0,
        allow_inf_nan=False,
    )

    planned_item_1_count: int = Field(ge=0)
    planned_item_2_count: int = Field(ge=0)
    planned_item_75_count: int = Field(ge=0)


class MethodPredictionInput(BaseModel):
    length_m: float = Field(ge=0, allow_inf_nan=False)
    width_m: float = Field(ge=0, allow_inf_nan=False)
    depth_m: float = Field(ge=0, allow_inf_nan=False)
    area_sqm: float = Field(ge=0, allow_inf_nan=False)
    count: float = Field(ge=0, allow_inf_nan=False)


class CostPredictionInput(BaseModel):
    depth_m: float = Field(ge=0, allow_inf_nan=False)
    area_sqm: float = Field(ge=0, allow_inf_nan=False)
    count: float = Field(ge=0, allow_inf_nan=False)

    times_per_year_frequency: float = Field(
        ge=0,
        allow_inf_nan=False,
    )

    density_kg_m3: float = Field(
        ge=0,
        allow_inf_nan=False,
    )

    length_m: float = Field(ge=0, allow_inf_nan=False)
    width_m: float = Field(ge=0, allow_inf_nan=False)

    calculated_work_area_sqm: float = Field(
        ge=0,
        allow_inf_nan=False,
    )

    # Important: saved model expects string item codes.
    item_code: str = Field(min_length=1)

    units: str = Field(min_length=1)


# --------------------------------------------------
# General API endpoints
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "application": "RoadWise AI",
        "message": "Backend API is running successfully",
        "status": "online",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RoadWise AI Backend",
    }


@app.get("/api/models/status")
def get_model_status():
    return {
        "total_models": len(MODEL_FILES),
        "loaded_models": len(loaded_models),
        "models": model_status,
    }


# --------------------------------------------------
# Repair Priority Prediction
# --------------------------------------------------

@app.post("/api/predict/priority")
def predict_priority(data: PriorityPredictionInput):
    model = loaded_models.get("repair_priority")

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Repair Priority model is unavailable",
        )

    input_values = data.model_dump()

    input_df = pd.DataFrame(
        [[input_values[name] for name in PRIORITY_FEATURES]],
        columns=PRIORITY_FEATURES,
    )

    try:
        prediction = model.predict(input_df)[0]
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}",
        ) from error

    return {
        "prediction": str(prediction),
        "prediction_type": "provisional_maintenance_inspection_priority",
        "model": MODEL_FILES["repair_priority"],
    }


# --------------------------------------------------
# Repair Method Prediction
# --------------------------------------------------

@app.post("/api/predict/method")
def predict_method(data: MethodPredictionInput):
    model = loaded_models.get("repair_method")

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Repair Method model is unavailable",
        )

    input_df = pd.DataFrame(
        [[
            data.length_m,
            data.width_m,
            data.depth_m,
            data.area_sqm,
            data.count,
        ]],
        columns=METHOD_FEATURES,
    )

    try:
        predicted_code = int(model.predict(input_df)[0])
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}",
        ) from error

    return {
        "repair_method_code": predicted_code,
        "repair_method": REPAIR_METHOD_NAMES.get(
            predicted_code,
            "Unknown Repair Method",
        ),
        "model": MODEL_FILES["repair_method"],
    }


# --------------------------------------------------
# Repair Cost Prediction
# --------------------------------------------------

@app.post("/api/predict/cost")
def predict_cost(data: CostPredictionInput):
    model = loaded_models.get("repair_cost")

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Repair Cost model is unavailable",
        )

    # Verify categories learned by the trained model.
    if data.item_code not in VALID_COST_ITEM_CODES:
        raise HTTPException(
            status_code=422,
            detail="Item Code was not present in model training data",
        )

    if data.units not in VALID_COST_UNITS:
        raise HTTPException(
            status_code=422,
            detail="Units value was not present in model training data",
        )

    input_df = pd.DataFrame(
        [[
            data.depth_m,
            data.area_sqm,
            data.count,
            data.times_per_year_frequency,
            data.density_kg_m3,
            data.length_m,
            data.width_m,
            data.calculated_work_area_sqm,
            data.item_code,
            data.units,
        ]],
        columns=COST_FEATURES,
    )

    try:
        predicted_cost = float(model.predict(input_df)[0])
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}",
        ) from error

    return {
        "predicted_cost_lkr": round(predicted_cost, 2),
        "currency": "LKR",
        "model": MODEL_FILES["repair_cost"],
    }
