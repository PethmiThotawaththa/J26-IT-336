"""
datasets.py
-----------
Dataset Management, Validation & Inspection REST API for Component 4.
"""

import os
import glob
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.app.core.config import settings

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("")
def list_datasets():
    """Lists all available research datasets, sources, sizes, and schema compliance."""
    datasets_meta = [
        {
            "name": "RDA Road Survey GPS & Chainage",
            "file": "data/processed/road_sections_master.csv",
            "type": "Real-World Field Data",
            "source": "Road Development Authority (RDA) Sri Lanka — Pavement Survey Vehicle",
            "records": 675,
            "description": "Standardized 100m engineering segments across 6 Colombo highways with GPS coordinates, elevation, and chainage."
        },
        {
            "name": "Historical Longitudinal Inspections",
            "file": "data/processed/longitudinal_inspections.csv",
            "type": "Longitudinal Time-Series",
            "source": "AASHTO/LTPP Deterioration Mechanics calibrated with RDA Baseline",
            "records": 3375,
            "description": "5 annual inspection cycles (2021-2025) tracking PCI, crack density, rutting, and IRI roughness."
        },
        {
            "name": "Engineered Deterioration Features",
            "file": "data/processed/deterioration_features.csv",
            "type": "Machine Learning Feature Matrix",
            "source": "Harmonized Traffic ESAL, Weather, Structural Number, and Distress Index",
            "records": 675,
            "description": "Curated feature matrix with multi-horizon prediction targets (3m, 6m, 12m, 24m) and risk classes."
        },
        {
            "name": "Classified Vehicle Traffic Counts",
            "file": "RDA/Traffic Data of Roads (B047, B174, B214, B240, B263 and B435).xlsx",
            "type": "Real-World Sensor Counts",
            "source": "RDA Traffic Engineering Division",
            "records": 39,
            "description": "16 vehicle categories (MCL, CAR, LGV, MG1, MG2, HG3, AG3-AG6) converted to AASHTO 18-kip ESALs."
        },
        {
            "name": "Colombo Meteorological Weather Telemetry",
            "file": "RDA/Whether.csv",
            "type": "Real-World Meteorological Data",
            "source": "Department of Meteorology / DWD MOSMIX Station Colombo",
            "records": 365,
            "description": "Daily precipitation (rainfall mm), temperature min/max/mean, relative humidity, wind speed, pressure."
        },
        {
            "name": "Highway Schedule of Rates (HSR 2025) Maintenance Budget",
            "file": "RDA/Forecasted routine maintenance budget 2026.xlsx",
            "type": "Real-World Engineering Budget",
            "source": "Ministry of Transport, Highways, Ports and Civil Aviation, Sri Lanka",
            "records": 123,
            "description": "Itemized unit costs (LKR) for asphalt patching, crack sealing, slurry seals, overlays, and reconstruction."
        },
        {
            "name": "Synthetic Pipeline Benchmark (Module B)",
            "file": "data/processed/synthetic_pipeline_benchmark.csv",
            "type": "Synthetic Validation Prototype",
            "source": "AASHTO Parametric Generator (Explicitly labelled per Module B)",
            "records": 2500,
            "description": "Synthetic dataset created to validate pipeline scalability and boundary conditions."
        }
    ]
    
    # Check file sizes
    for item in datasets_meta:
        full_path = os.path.join(settings.BASE_DIR, item["file"])
        if os.path.exists(full_path):
            item["file_size_kb"] = round(os.path.getsize(full_path) / 1024.0, 1)
            item["status"] = "AVAILABLE"
        else:
            item["file_size_kb"] = 0.0
            item["status"] = "MISSING"
            
    return {"datasets": datasets_meta}

@router.get("/preview")
def preview_dataset(file_key: str = "features"):
    """Returns the top rows and summary schema of the selected dataset."""
    path_map = {
        "features": os.path.join(settings.DATA_PROCESSED, "deterioration_features.csv"),
        "sections": os.path.join(settings.DATA_PROCESSED, "road_sections_master.csv"),
        "inspections": os.path.join(settings.DATA_PROCESSED, "longitudinal_inspections.csv"),
        "synthetic": os.path.join(settings.DATA_PROCESSED, "synthetic_pipeline_benchmark.csv")
    }
    
    target_path = path_map.get(file_key)
    if not target_path or not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"Dataset key '{file_key}' not found.")
        
    df = pd.read_csv(target_path)
    # Replace NaN with None for clean JSON serialization
    df_clean = df.where(pd.notnull(df), None)
    
    return {
        "dataset_key": file_key,
        "total_rows": len(df),
        "columns": df.columns.tolist(),
        "preview_rows": df_clean.head(10).to_dict(orient="records"),
        "numeric_summary": df.describe().to_dict()
    }
