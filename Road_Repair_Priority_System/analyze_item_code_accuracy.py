
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
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Define project paths
project = Path(__file__).resolve().parent

data_file = project / "outputs" / "ml_cost_dataset.csv"

summary_file = (
    project / "outputs" / "item_code_accuracy_summary.csv"
)

predictions_file = (
    project / "outputs" / "item_code_accuracy_predictions.csv"
)


# Check dataset
if not data_file.exists():
    raise FileNotFoundError(
        "Dataset not found: outputs/ml_cost_dataset.csv"
    )


# Load historical data
data = pd.read_csv(data_file)

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

categorical_features = [
    "Item Code",
    "Units",
]

required_columns = [
    "RoadID",
    "Repair_Cost_LKR",
    *[feature for feature in numeric_features
      if feature != "Calculated_Work_Area_sqm"],
    *categorical_features,
]

missing_columns = [
    col for col in required_columns
    if col not in data.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# Normalize categorical features
data["RoadID"] = (
    data["RoadID"].astype(str).str.strip()
)

data["Item Code"] = (
    data["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

data["Units"] = (
    data["Units"].astype(str).str.strip()
)


# Convert numeric columns
for feature in numeric_features:

    if feature == "Calculated_Work_Area_sqm":
        continue

    data[feature] = pd.to_numeric(
        data[feature],
        errors="coerce",
    )

data["Repair_Cost_LKR"] = pd.to_numeric(
    data["Repair_Cost_LKR"],
    errors="coerce",
)


# Calculate work area
data["Calculated_Work_Area_sqm"] = (
    data["Length (m)"] * data["Width (m)"]
)


# Validate dataset
features = numeric_features + categorical_features

if data[features].isna().any().any():
    raise ValueError(
        "Dataset contains missing feature values."
    )

if data["Repair_Cost_LKR"].isna().any():
    raise ValueError(
        "Dataset contains missing repair costs."
    )

if not np.isfinite(
    data[numeric_features + ["Repair_Cost_LKR"]]
    .to_numpy(dtype=float)
).all():
    raise ValueError(
        "Dataset contains non-finite numeric values."
    )


# Prepare features, target and road groups
X = data[features]
y = data["Repair_Cost_LKR"]
groups = data["RoadID"]


# Define the ML model
def create_model():

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

    regressor = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", regressor),
        ]
    )


# Perform Leave-One-Road-Out validation
logo = LeaveOneGroupOut()

predictions = np.full(
    len(data),
    np.nan,
    dtype=float,
)

print("=" * 65)
print("ML MODEL ACCURACY BY REPAIR ITEM CODE")
print("=" * 65)

print(f"\nTotal records: {len(data)}")
print(f"Total roads: {groups.nunique()}")
print(f"Total Item Codes: {data['Item Code'].nunique()}")

print("\nValidation: Leave-One-Road-Out")
print("Model: Gradient Boosting without Road ID")

print("\nRunning cross-validation...")

for train_index, test_index in logo.split(
    X,
    y,
    groups=groups,
):

    model = create_model()

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]

    y_train = y.iloc[train_index]

    test_road = groups.iloc[test_index].iloc[0]

    model.fit(
        X_train,
        y_train,
    )

    fold_predictions = model.predict(X_test)

    predictions[test_index] = fold_predictions

    print(
        f"Completed road {test_road}: "
        f"{len(test_index)} test records"
    )


# Calculate prediction errors
results = data[
    [
        "RoadID",
        "Item Code",
        "Units",
        "Length (m)",
        "Width (m)",
        "Calculated_Work_Area_sqm",
        "Repair_Cost_LKR",
    ]
].copy()

results["ML_Predicted_Cost_LKR"] = predictions

results["Absolute_Error_LKR"] = (
    results["Repair_Cost_LKR"]
    - results["ML_Predicted_Cost_LKR"]
).abs()


# Calculate overall performance
overall_mae = mean_absolute_error(
    results["Repair_Cost_LKR"],
    results["ML_Predicted_Cost_LKR"],
)

overall_rmse = np.sqrt(
    mean_squared_error(
        results["Repair_Cost_LKR"],
        results["ML_Predicted_Cost_LKR"],
    )
)

overall_r2 = r2_score(
    results["Repair_Cost_LKR"],
    results["ML_Predicted_Cost_LKR"],
)


print("\n" + "=" * 65)
print("1. OVERALL MODEL PERFORMANCE")
print("=" * 65)

print(f"\nOverall MAE: Rs. {overall_mae:,.2f}")
print(f"Overall RMSE: Rs. {overall_rmse:,.2f}")
print(f"Overall R2 Score: {overall_r2:.4f}")


# Calculate accuracy summary for each Item Code
summary_rows = []

for item_code, item_data in results.groupby(
    "Item Code"
):

    actual = item_data["Repair_Cost_LKR"]
    predicted = item_data["ML_Predicted_Cost_LKR"]

    count = len(item_data)

    mae = mean_absolute_error(
        actual,
        predicted,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted,
        )
    )

    mean_actual = actual.mean()

    relative_mae = (
        mae / mean_actual * 100
        if mean_actual > 0
        else np.nan
    )

    summary_rows.append(
        {
            "Item Code": item_code,
            "Record Count": count,
            "Road Count": item_data[
                "RoadID"
            ].nunique(),
            "Mean Actual Cost LKR": mean_actual,
            "MAE LKR": mae,
            "RMSE LKR": rmse,
            "Relative MAE Percent": relative_mae,
        }
    )


summary = pd.DataFrame(summary_rows)

summary = summary.sort_values(
    by="MAE LKR",
    ascending=False,
)


# Print item-level performance
print("\n" + "=" * 65)
print("2. MODEL ERRORS BY ITEM CODE")
print("=" * 65)

print(
    summary.to_string(
        index=False,
        float_format=lambda x: f"{x:,.2f}",
    )
)


# Detailed analysis for Item Codes 51 and 69
for selected_code in ["51", "69"]:

    print("\n" + "=" * 65)
    print(
        f"3. DETAILED PREDICTIONS - ITEM CODE "
        f"{selected_code}"
    )
    print("=" * 65)

    selected = results[
        results["Item Code"] == selected_code
    ].copy()

    if selected.empty:

        print("No historical records found.")
        continue

    print(
        selected[
            [
                "RoadID",
                "Calculated_Work_Area_sqm",
                "Repair_Cost_LKR",
                "ML_Predicted_Cost_LKR",
                "Absolute_Error_LKR",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}",
        )
    )

    print(
        "\nItem Code MAE: Rs. "
        f"{selected['Absolute_Error_LKR'].mean():,.2f}"
    )


# Identify item codes needing attention
print("\n" + "=" * 65)
print("4. ITEM CODES WITH HIGHEST ERRORS")
print("=" * 65)

top_errors = summary.head(5)

print(
    top_errors[
        [
            "Item Code",
            "Record Count",
            "MAE LKR",
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:,.2f}",
    )
)


# Save reports
summary.to_csv(
    summary_file,
    index=False,
)

results.to_csv(
    predictions_file,
    index=False,
)

print("\n" + "=" * 65)
print("5. SAVED REPORTS")
print("=" * 65)

print(f"\nSummary: {summary_file}")
print(f"Predictions: {predictions_file}")

print("\nITEM CODE ACCURACY ANALYSIS COMPLETED!")
