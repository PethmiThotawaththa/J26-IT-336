
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# File locations
# --------------------------------------------------

DATA_FILE = Path("outputs/ml_cost_dataset.csv")

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = (
    MODEL_DIR / "final_extra_trees_cost_model.joblib"
)


# --------------------------------------------------
# Load and prepare historical data
# --------------------------------------------------

df = pd.read_csv(DATA_FILE)

df["Item Code"] = (
    pd.to_numeric(df["Item Code"], errors="coerce")
    .astype("Int64")
    .astype(str)
)

df["Units"] = df["Units"].astype(str).str.strip()

df["Calculated_Work_Area_sqm"] = (
    df["Length (m)"].fillna(0)
    * df["Width (m)"].fillna(0)
)


# --------------------------------------------------
# Define ML input features
# Chainage and RoadID are intentionally excluded.
# --------------------------------------------------

numeric_features = [
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Length (m)",
    "Width (m)",
    "Calculated_Work_Area_sqm",
]

categorical_features = [
    "Item Code",
    "Units",
]

input_features = (
    numeric_features + categorical_features
)


# --------------------------------------------------
# Build machine learning pipeline
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            "passthrough",
            numeric_features,
        ),
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
    ]
)

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "regressor",
            ExtraTreesRegressor(
                n_estimators=300,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)


# --------------------------------------------------
# Train on all available historical records
# --------------------------------------------------

X = df[input_features]
y = df["Repair_Cost_LKR"]

model.fit(X, y)


# --------------------------------------------------
# Save trained model and feature information
# --------------------------------------------------

model_package = {
    "model": model,
    "input_features": input_features,
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,
    "model_name": "Extra Trees Without Chainage",
    "training_records": len(df),
}

joblib.dump(model_package, MODEL_FILE)


# --------------------------------------------------
# Training summary
# --------------------------------------------------

print("=" * 60)
print("FINAL ML REPAIR COST MODEL")
print("=" * 60)

print("\nAlgorithm: Extra Trees Regressor")
print("Chainage features: Excluded")
print("Road ID feature: Excluded")

print(f"\nTraining records: {len(df)}")
print(f"Unique repair item codes: {df['Item Code'].nunique()}")

print("\nInput features:")
for feature in input_features:
    print(f"  - {feature}")

print(f"\nModel saved successfully: {MODEL_FILE}")

print("\nPrevious Gradient Boosting model was NOT modified.")
print("Model predicts historical-pattern repair cost estimates.")
print("Training on all records is not an accuracy evaluation.")
