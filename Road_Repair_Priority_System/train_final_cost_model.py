
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Define project paths
project = Path(__file__).parent

data_file = project / "outputs" / "ml_cost_dataset.csv"

model_dir = project / "models"
model_dir.mkdir(exist_ok=True)

model_file = model_dir / "repair_cost_model.joblib"


# Load historical repair data
df = pd.read_csv(data_file)


# Create the engineered work-area feature
df["Calculated_Work_Area_sqm"] = (
    df["Length (m)"] * df["Width (m)"]
)


# Define numerical features
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
    "Calculated_Work_Area_sqm"
]


# Define categorical features
categorical_features = [
    "RoadID",
    "Item Code",
    "Units"
]


# Prepare model inputs and prediction target
feature_columns = numeric_features + categorical_features

X = df[feature_columns].copy()
y = df["Repair_Cost_LKR"]

for column in categorical_features:
    X[column] = X[column].astype(str)


# Prepare categorical encoding and numerical inputs
preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            "passthrough",
            numeric_features
        ),
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ]
)


# Create the selected machine learning model
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                random_state=42
            )
        )
    ]
)


# Train the model using all available historical records
model.fit(X, y)


# Save the complete trained pipeline
joblib.dump(model, model_file)


# Display training information
print("ML COST MODEL TRAINING")
print("======================")

print("Algorithm: Gradient Boosting Regressor")
print("Training records:", len(df))
print("Training roads:", df["RoadID"].nunique())
print("Input features:", len(feature_columns))

print("\nMODEL INPUT FEATURES")
print("====================")

for feature in feature_columns:
    print("-", feature)

print("\nMODEL SAVED SUCCESSFULLY")
print("========================")

print("Model file:", model_file)
print("\nTRAINING COMPLETED!")
