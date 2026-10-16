
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Define project paths
project = Path(__file__).parent

data_file = project / "outputs" / "ml_cost_dataset.csv"

output_file = (
    project / "outputs" / "feature_comparison_predictions.csv"
)


# Load the historical repair dataset
df = pd.read_csv(data_file)


# Create a new engineering feature
df["Calculated_Work_Area_sqm"] = (
    df["Length (m)"] * df["Width (m)"]
)


# Define the original numerical features
original_numeric_features = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)"
]


# Define categorical features
categorical_features = [
    "RoadID",
    "Item Code",
    "Units"
]


# Define the improved feature set
improved_numeric_features = (
    original_numeric_features
    + ["Calculated_Work_Area_sqm"]
)


# Prepare the prediction target
y = df["Repair_Cost_LKR"]

# Group records by road for validation
groups = df["RoadID"].astype(str)


# Create and evaluate a Random Forest model
def evaluate_feature_set(name, numeric_features):

    feature_columns = (
        numeric_features + categorical_features
    )

    X = df[feature_columns].copy()

    for column in categorical_features:
        X[column] = X[column].astype(str)

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

    model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=200,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
            )
        ]
    )

    logo = LeaveOneGroupOut()

    predictions = np.zeros(len(df))

    # Train on five roads and test on the remaining road
    for train_idx, test_idx in logo.split(X, y, groups):

        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]

        y_train = y.iloc[train_idx]

        model.fit(X_train, y_train)

        predictions[test_idx] = model.predict(X_test)

    # Calculate overall validation metrics
    mae = mean_absolute_error(y, predictions)

    rmse = np.sqrt(
        mean_squared_error(y, predictions)
    )

    r2 = r2_score(y, predictions)

    print(f"\nMODEL: {name}")
    print(f"MAE (LKR): {mae:.2f}")
    print(f"RMSE (LKR): {rmse:.2f}")
    print(f"R2 Score: {r2:.4f}")

    return predictions


# Evaluate the original Random Forest feature set
print("ML FEATURE ENGINEERING EXPERIMENT")
print("=================================")

print("Total records:", len(df))
print("Total roads:", groups.nunique())

original_predictions = evaluate_feature_set(
    "Original Random Forest",
    original_numeric_features
)


# Evaluate Random Forest with the new area feature
improved_predictions = evaluate_feature_set(
    "Random Forest With Calculated Work Area",
    improved_numeric_features
)


# Save both sets of predictions
results = pd.DataFrame({
    "RoadID": df["RoadID"],
    "Item_Code": df["Item Code"],
    "Actual_Cost_LKR": y,
    "Original_RF_Predicted_LKR": original_predictions,
    "Improved_RF_Predicted_LKR": improved_predictions
})

results["Original_Absolute_Error_LKR"] = abs(
    results["Actual_Cost_LKR"]
    - results["Original_RF_Predicted_LKR"]
)

results["Improved_Absolute_Error_LKR"] = abs(
    results["Actual_Cost_LKR"]
    - results["Improved_RF_Predicted_LKR"]
)

results.to_csv(
    output_file,
    index=False
)

print("\nSaved predictions:", output_file)
print("\nML FEATURE EXPERIMENT COMPLETED!")
