
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Define project paths
project = Path(__file__).resolve().parent

data_file = project / "outputs" / "ml_cost_dataset.csv"

model_file = (
    project / "models" / "repair_cost_model_without_road_id.joblib"
)


# Load the historical repair cost dataset
if not data_file.exists():
    raise FileNotFoundError(
        "Dataset not found. Run prepare_ml_cost_dataset.py first."
    )

data = pd.read_csv(data_file)


print("=" * 60)
print("TRAIN ML COST MODEL WITHOUT ROAD ID")
print("=" * 60)

print(f"\nTotal repair records: {len(data)}")
print(f"Total roads: {data['RoadID'].nunique()}")


# Create the engineered work area feature
# This is an input feature, not a cost calculation formula
data["Length (m)"] = pd.to_numeric(
    data["Length (m)"],
    errors="coerce",
)

data["Width (m)"] = pd.to_numeric(
    data["Width (m)"],
    errors="coerce",
)

data["Calculated_Work_Area_sqm"] = (
    data["Length (m)"] * data["Width (m)"]
)


# Define numeric input features
numeric_features = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Calculated_Work_Area_sqm",
]


# Define categorical input features
# RoadID is intentionally excluded
categorical_features = [
    "Item Code",
    "Units",
]


# Define the target
target = "Repair_Cost_LKR"


# Validate dataset columns
required_columns = (
    numeric_features
    + categorical_features
    + ["RoadID", target]
)

missing_columns = (
    set(required_columns) - set(data.columns)
)

if missing_columns:
    raise ValueError(
        f"Missing dataset columns: {sorted(missing_columns)}"
    )


# Convert numeric values
for column in numeric_features + [target]:
    data[column] = pd.to_numeric(
        data[column],
        errors="coerce",
    )


# Reject missing or infinite numeric values
numeric_values = data[
    numeric_features + [target]
].to_numpy(dtype=float)

if not np.isfinite(numeric_values).all():
    raise ValueError(
        "Dataset contains missing or invalid numeric values."
    )


# Convert categorical values to text
data["Item Code"] = (
    data["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

data["Units"] = (
    data["Units"]
    .astype(str)
    .str.strip()
)


# Validate categorical values
for column in categorical_features:
    invalid_values = (
        data[column].isin(["", "nan", "None"])
    )

    if invalid_values.any():
        raise ValueError(
            f"Invalid categorical values found in {column}."
        )


# Prepare training inputs and target
input_features = (
    numeric_features + categorical_features
)

X = data[input_features]
y = data[target]


# Prepare numeric and categorical features
preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            "passthrough",
            numeric_features,
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features,
        ),
    ]
)


# Create the Gradient Boosting ML model
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "regressor",
            GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                random_state=42,
            ),
        ),
    ]
)


# Train the ML model using all historical records
print("\nTraining Gradient Boosting model...")

model.fit(X, y)

print("Model training completed successfully.")


# Save the trained model
model_file.parent.mkdir(
    parents=True,
    exist_ok=True,
)

joblib.dump(model, model_file)


# Display model information
print("\n" + "=" * 60)
print("TRAINING SUMMARY")
print("=" * 60)

print(f"Training records: {len(X)}")
print(f"Numeric features: {len(numeric_features)}")
print(f"Categorical features: {len(categorical_features)}")

print("\nCategorical features used:")
for feature in categorical_features:
    print(f" - {feature}")

print("\nRoad ID used as ML input: NO")

print("\nModel type: Gradient Boosting Regressor")

print("\nSaved trained model to:")
print(model_file)

print("\nIMPORTANT:")
print(
    "This model was trained on all available historical records."
)
print(
    "Its generalization performance was evaluated separately "
    "using Leave-One-Road-Out validation."
)

print("\nMODEL TRAINING COMPLETED!")
