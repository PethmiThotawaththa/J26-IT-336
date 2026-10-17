
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Define project paths
project = Path(__file__).resolve().parent

data_file = project / "outputs" / "ml_cost_dataset.csv"
output_file = project / "outputs" / "road_id_feature_comparison.csv"
prediction_file = (
    project / "outputs" / "road_id_comparison_predictions.csv"
)


# Load the prepared ML dataset
if not data_file.exists():
    raise FileNotFoundError(
        "Dataset not found. Run prepare_ml_cost_dataset.py first."
    )

data = pd.read_csv(data_file)


print("=" * 60)
print("STEP 16 - ROAD ID FEATURE COMPARISON")
print("=" * 60)


# Create the engineered area feature
# This is an ML input feature, not a repair cost formula
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


print(f"\nTotal repair records: {len(data)}")
print(f"Total roads: {data['RoadID'].nunique()}")


# Define the prediction target
target = "Repair_Cost_LKR"


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


# Define two ML model configurations
configurations = {
    "With Road ID": [
        "RoadID",
        "Item Code",
        "Units",
    ],
    "Without Road ID": [
        "Item Code",
        "Units",
    ],
}


# Check that required columns exist
required_columns = set(
    numeric_features
    + ["RoadID", "Item Code", "Units", target]
)

missing_columns = required_columns - set(data.columns)

if missing_columns:
    raise ValueError(
        f"Missing dataset columns: {sorted(missing_columns)}"
    )


# Convert numeric columns
for column in numeric_features + [target]:
    data[column] = pd.to_numeric(
        data[column],
        errors="coerce",
    )


# Check for invalid numeric values
if not np.isfinite(
    data[numeric_features + [target]].to_numpy(
        dtype=float
    )
).all():
    raise ValueError(
        "Dataset contains missing or invalid numeric values."
    )


# Convert categorical columns to text
data["RoadID"] = data["RoadID"].astype(str).str.strip()

data["Item Code"] = (
    data["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

data["Units"] = data["Units"].astype(str).str.strip()


# Check categorical values
if (
    data[["RoadID", "Item Code", "Units"]]
    .isin(["", "nan", "None"])
    .any()
    .any()
):
    raise ValueError(
        "Dataset contains missing categorical values."
    )


# Prepare result containers
comparison_results = []
all_predictions = []


# Compare models using Leave-One-Road-Out validation
for model_name, categorical_features in configurations.items():

    print("\n" + "-" * 60)
    print(f"TESTING: {model_name}")
    print("-" * 60)

    input_features = numeric_features + categorical_features

    actual_values = []
    predicted_values = []

    for test_road in sorted(data["RoadID"].unique()):

        # Keep one complete road for testing
        train_data = data[data["RoadID"] != test_road]
        test_data = data[data["RoadID"] == test_road]

        X_train = train_data[input_features]
        y_train = train_data[target]

        X_test = test_data[input_features]
        y_test = test_data[target]

        # Prepare the ML input features
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

        # Create a fresh ML model for each validation fold
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

        # Train the model on the other roads
        model.fit(X_train, y_train)

        # Predict costs for the unseen road
        predictions = model.predict(X_test)

        actual_values.extend(y_test.to_numpy())
        predicted_values.extend(predictions)

        road_mae = mean_absolute_error(
            y_test,
            predictions,
        )

        print(
            f"{test_road}: "
            f"{len(test_data)} records | "
            f"MAE = Rs. {road_mae:,.2f}"
        )

        # Store individual predictions
        for row_index, actual, predicted in zip(
            test_data.index,
            y_test,
            predictions,
        ):
            all_predictions.append(
                {
                    "Model": model_name,
                    "RoadID": test_road,
                    "RowIndex": int(row_index),
                    "Item Code": data.loc[
                        row_index, "Item Code"
                    ],
                    "Actual_Cost_LKR": float(actual),
                    "Predicted_Cost_LKR": float(predicted),
                    "Absolute_Error_LKR": abs(
                        float(actual) - float(predicted)
                    ),
                }
            )

    # Calculate overall validation metrics
    mae = mean_absolute_error(
        actual_values,
        predicted_values,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual_values,
            predicted_values,
        )
    )

    r2 = r2_score(
        actual_values,
        predicted_values,
    )

    comparison_results.append(
        {
            "Model": model_name,
            "MAE_LKR": mae,
            "RMSE_LKR": rmse,
            "R2_Score": r2,
        }
    )

    print(f"\nOverall MAE: Rs. {mae:,.2f}")
    print(f"Overall RMSE: Rs. {rmse:,.2f}")
    print(f"Overall R2: {r2:.4f}")


# Create the final comparison table
results_df = pd.DataFrame(comparison_results)

results_df = results_df.sort_values(
    by="MAE_LKR",
    ascending=True,
)


# Save experiment outputs
output_file.parent.mkdir(
    parents=True,
    exist_ok=True,
)

results_df.to_csv(
    output_file,
    index=False,
)

predictions_df = pd.DataFrame(all_predictions)

predictions_df.to_csv(
    prediction_file,
    index=False,
)


# Display final results
print("\n" + "=" * 60)
print("FINAL MODEL COMPARISON")
print("=" * 60)

print(
    results_df.to_string(
        index=False,
        float_format=lambda value: f"{value:,.4f}",
    )
)

best_model = results_df.iloc[0]["Model"]

print(f"\nLowest MAE model: {best_model}")

print("\nSaved comparison results to:")
print(output_file)

print("\nSaved detailed predictions to:")
print(prediction_file)

print("\nEXPERIMENT COMPLETED!")
