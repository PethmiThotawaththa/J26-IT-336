"""
features.py
-----------
Feature engineering, validation, and reusable scikit-learn preprocessing pipelines
for Component 4: AI-Based Predictive Road Maintenance.
Ensures zero data leakage by fitting transformers strictly on training sets.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

# Base raw feature list expected from input data
RAW_FEATURE_COLUMNS = [
    "current_pci",
    "pavement_age_years",
    "structural_number",
    "aadt",
    "daily_esal",
    "heavy_vehicle_pct",
    "annual_precipitation_mm",
    "mean_temp_c",
    "mean_diurnal_range_c",
    "monsoon_risk_factor",
    "historical_decay_rate_annual",
    "crack_density_pct",
    "pothole_count",
    "iri_roughness",
    "rut_depth_mm"
]

ENGINEERED_FEATURE_COLUMNS = [
    "traffic_precipitation_interaction",
    "heavy_traffic_load_ratio",
    "distress_composite_index",
    "climate_fatigue_index"
]

ALL_FEATURE_COLUMNS = RAW_FEATURE_COLUMNS + ENGINEERED_FEATURE_COLUMNS

class PavementFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible transformer that constructs pavement degradation indicators:
    - traffic_precipitation_interaction: Axle load compounded with monsoon water ingress
    - heavy_traffic_load_ratio: Daily ESAL normalized by structural number
    - distress_composite_index: Combined surface distress score
    - climate_fatigue_index: Diurnal temperature delta x precipitation
    """
    def __init__(self):
        self.feature_names_ = ALL_FEATURE_COLUMNS
        
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X, columns=RAW_FEATURE_COLUMNS)
        else:
            X_df = X.copy()
            
        # Ensure raw columns exist with defaults if missing
        for col in RAW_FEATURE_COLUMNS:
            if col not in X_df.columns:
                X_df[col] = np.nan
                
        # Compute engineered features
        # 1. Traffic x Monsoon interaction (water ingress under dynamic axle load)
        X_df["traffic_precipitation_interaction"] = (
            X_df["daily_esal"] * X_df["monsoon_risk_factor"]
        )
        
        # 2. Structural load ratio
        sn = X_df["structural_number"].clip(lower=1.5)
        X_df["heavy_traffic_load_ratio"] = X_df["daily_esal"] / sn
        
        # 3. Composite distress index
        cracks = X_df["crack_density_pct"].fillna(0.0)
        potholes = X_df["pothole_count"].fillna(0.0)
        rutting = X_df["rut_depth_mm"].fillna(0.0)
        X_df["distress_composite_index"] = (
            cracks * 0.4 + potholes * 3.5 + rutting * 0.8
        )
        
        # 4. Climate thermal-moisture fatigue
        precip = X_df["annual_precipitation_mm"].fillna(1500.0)
        diurnal = X_df["mean_diurnal_range_c"].fillna(6.0)
        X_df["climate_fatigue_index"] = (precip * diurnal) / 1000.0
        
        return X_df[ALL_FEATURE_COLUMNS].to_numpy()

def build_preprocessing_pipeline() -> Pipeline:
    """
    Constructs a leak-free preprocessing pipeline:
    1. PavementFeatureEngineer: Derives physical pavement indicators.
    2. SimpleImputer: Imputes any remaining missing values using training medians.
    3. StandardScaler: Normalizes feature scales for distance-sensitive and linear algorithms.
    """
    pipeline = Pipeline(steps=[
        ("engineer", PavementFeatureEngineer()),
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    return pipeline

def save_pipeline(pipeline: Pipeline, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(pipeline, filepath)

def load_pipeline(filepath: str) -> Pipeline:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Preprocessing pipeline not found at {filepath}")
    return joblib.load(filepath)
