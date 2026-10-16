
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
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
output_file = project / "outputs" / "road_validation_predictions.csv"


# Load the prepared ML dataset
df = pd.read_csv(data_file)


# Define numerical input features
numeric_features = [
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


# Define categorical input features
categorical_features = [
    "RoadID",
    "Item Code",
    "Units"
]


# Separate model inputs and target
feature_columns = numeric_features + categorical_features

X = df[feature_columns].copy()
y = df["Repair_Cost_LKR"]


# Use road IDs to create validation groups
groups = df["RoadID"].astype(str)


# Convert categorical features to strings
for column in categorical_features:
    X[column] = X[column].astype(str)


# Create the preprocessing pipeline
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


# Create the Random Forest prediction pipeline
random_forest = Pipeline(
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


# Create a simple comparison model
dummy_model = DummyRegressor(strategy="median")


# Prepare leave-one-road-out validation
logo = LeaveOneGroupOut()

all_results = []


# Print experiment information
print("ROAD-BASED COST MODEL VALIDATION")
print("================================")
print("Total records:", len(df))
print("Total roads:", groups.nunique())


# Train and test using one held-out road at a time
for train_idx, test_idx in logo.split(X, y, groups):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    test_road = groups.iloc[test_idx].iloc[0]

    # Train models using the other roads
    dummy_model.fit(X_train, y_train)
    random_forest.fit(X_train, y_train)

    # Predict costs for the held-out road
    dummy_predictions = dummy_model.predict(X_test)
    rf_predictions = random_forest.predict(X_test)

    # Calculate the error for this road
    dummy_mae = mean_absolute_error(
        y_test,
        dummy_predictions
    )

    rf_mae = mean_absolute_error(
        y_test,
        rf_predictions
    )

    print(f"\nTEST ROAD: {test_road}")
    print("Test records:", len(test_idx))
    print(f"Dummy MAE (LKR): {dummy_mae:.2f}")
    print(f"Random Forest MAE (LKR): {rf_mae:.2f}")

    # Keep original repair details for error analysis
    fold_results = df.iloc[test_idx].copy()

    # Add actual and predicted repair costs
    fold_results["Actual_Cost_LKR"] = y_test.values
    fold_results["Dummy_Predicted_LKR"] = dummy_predictions
    fold_results["RF_Predicted_LKR"] = rf_predictions

    # Calculate absolute prediction errors
    fold_results["RF_Absolute_Error_LKR"] = abs(
        fold_results["Actual_Cost_LKR"]
        - fold_results["RF_Predicted_LKR"]
    )

    # Positive values mean overprediction
    # Negative values mean underprediction
    fold_results["RF_Signed_Error_LKR"] = (
        fold_results["RF_Predicted_LKR"]
        - fold_results["Actual_Cost_LKR"]
    )

    all_results.append(fold_results)


# Combine predictions from all roads
results = pd.concat(
    all_results,
    ignore_index=True
)


# Calculate overall evaluation metrics
def print_metrics(name, predictions):

    actual = results["Actual_Cost_LKR"]

    mae = mean_absolute_error(
        actual,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predictions
        )
    )

    r2 = r2_score(
        actual,
        predictions
    )

    print(f"\n{name}")
    print(f"MAE (LKR): {mae:.2f}")
    print(f"RMSE (LKR): {rmse:.2f}")
    print(f"R2 Score: {r2:.4f}")


# Display overall validation results
print("\nOVERALL ROAD-BASED VALIDATION")
print("=============================")

print_metrics(
    "Dummy Median Baseline",
    results["Dummy_Predicted_LKR"]
)

print_metrics(
    "Random Forest Regressor",
    results["RF_Predicted_LKR"]
)


# Display the records with the largest prediction errors
print("\nTOP 10 LARGEST RANDOM FOREST ERRORS")
print("===================================")

top_errors = results.nlargest(
    10,
    "RF_Absolute_Error_LKR"
)

display_columns = [
    "RoadID",
    "Item Code",
    "Units",
    "Length (m)",
    "Width (m)",
    "Area (sqm)",
    "Actual_Cost_LKR",
    "RF_Predicted_LKR",
    "RF_Absolute_Error_LKR"
]

print(
    top_errors[display_columns].to_string(
        index=False
    )
)


# Save detailed validation predictions
results.to_csv(
    output_file,
    index=False
)

print("\nSaved predictions:", output_file)
print("\nROAD-BASED ERROR ANALYSIS COMPLETED!")
