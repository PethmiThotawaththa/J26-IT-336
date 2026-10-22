import pytest
import numpy as np
import pandas as pd
from backend.app.ml.features import (
    RAW_FEATURE_COLUMNS,
    ALL_FEATURE_COLUMNS,
    PavementFeatureEngineer,
    build_preprocessing_pipeline
)

def test_raw_feature_columns_defined():
    assert len(RAW_FEATURE_COLUMNS) == 15
    assert "current_pci" in RAW_FEATURE_COLUMNS
    assert "daily_esal" in RAW_FEATURE_COLUMNS
    assert "monsoon_risk_factor" in RAW_FEATURE_COLUMNS

def test_feature_engineer_transformation():
    engineer = PavementFeatureEngineer()
    sample = pd.DataFrame([{
        "current_pci": 75.0,
        "pavement_age_years": 4.0,
        "structural_number": 4.0,
        "aadt": 25000,
        "daily_esal": 2000.0,
        "heavy_vehicle_pct": 6.5,
        "annual_precipitation_mm": 2500.0,
        "mean_temp_c": 28.0,
        "mean_diurnal_range_c": 5.0,
        "monsoon_risk_factor": 1.6,
        "historical_decay_rate_annual": 3.2,
        "crack_density_pct": 10.0,
        "pothole_count": 1,
        "iri_roughness": 2.5,
        "rut_depth_mm": 4.0
    }])
    
    transformed = engineer.fit_transform(sample)
    assert transformed.shape == (1, len(ALL_FEATURE_COLUMNS))
    
def test_preprocessing_pipeline_fit_and_leak_free():
    pipeline = build_preprocessing_pipeline()
    train_df = pd.DataFrame([{
        "current_pci": 80.0, "pavement_age_years": 3.0, "structural_number": 4.0,
        "aadt": 20000, "daily_esal": 1200.0, "heavy_vehicle_pct": 4.0,
        "annual_precipitation_mm": 2000.0, "mean_temp_c": 27.0, "mean_diurnal_range_c": 4.0,
        "monsoon_risk_factor": 1.2, "historical_decay_rate_annual": 2.5,
        "crack_density_pct": 2.0, "pothole_count": 0, "iri_roughness": 1.8, "rut_depth_mm": 2.0
    }, {
        "current_pci": 60.0, "pavement_age_years": 6.0, "structural_number": 3.5,
        "aadt": 30000, "daily_esal": 2500.0, "heavy_vehicle_pct": 8.0,
        "annual_precipitation_mm": 2800.0, "mean_temp_c": 29.0, "mean_diurnal_range_c": 5.5,
        "monsoon_risk_factor": 1.8, "historical_decay_rate_annual": 4.5,
        "crack_density_pct": 18.0, "pothole_count": 3, "iri_roughness": 3.8, "rut_depth_mm": 12.0
    }])
    
    # Fit strictly on train
    X_train = pipeline.fit_transform(train_df)
    assert X_train.shape == (2, len(ALL_FEATURE_COLUMNS))
    
    # Test on unseen single row
    test_df = train_df.iloc[[0]].copy()
    X_test = pipeline.transform(test_df)
    assert X_test.shape == (1, len(ALL_FEATURE_COLUMNS))
