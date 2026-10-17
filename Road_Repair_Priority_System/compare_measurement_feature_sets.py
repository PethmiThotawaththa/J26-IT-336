
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


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    PROJECT_DIR / "outputs" / "ml_cost_dataset.csv"
)

OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load and prepare dataset
# --------------------------------------------------

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

df["RoadID"] = (
    df["RoadID"].astype(str).str.strip()
)

df["Item Code"] = (
    df["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

df["Units"] = (
    df["Units"].astype(str).str.strip()
)

numeric_columns = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Repair_Cost_LKR",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )

df["Calculated_Work_Area_sqm"] = (
    df["Length (m)"] * df["Width (m)"]
)

# Use the same missing-value handling for all experiments.
df[numeric_columns] = df[numeric_columns].fillna(0)
df["Calculated_Work_Area_sqm"] = (
    df["Calculated_Work_Area_sqm"].fillna(0)
)

target_column = "Repair_Cost_LKR"

if df[target_column].isna().any():
    raise ValueError("Target column contains missing values.")


# --------------------------------------------------
# 3. Define feature sets
# --------------------------------------------------

common_numeric_features = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
]

categorical_features = [
    "Item Code",
    "Units",
]

feature_sets = {
    "A_Current_All_Three": (
        common_numeric_features
        + [
            "Length (m)",
            "Width (m)",
            "Calculated_Work_Area_sqm",
        ]
    ),
    "B_Work_Area_Only": (
        common_numeric_features
        + [
            "Calculated_Work_Area_sqm",
        ]
    ),
    "C_Length_Width_Only": (
        common_numeric_features
        + [
            "Length (m)",
            "Width (m)",
        ]
    ),
}


# --------------------------------------------------
# 4. ML model
# --------------------------------------------------

def build_model(numeric_features):

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


# --------------------------------------------------
# 5. Leave-One-Road-Out validation
# --------------------------------------------------

logo = LeaveOneGroupOut()

y = df[target_column]
groups = df["RoadID"]

summary_rows = []
prediction_frames = []


print("=" * 72)
print("STEP 24 - ML MEASUREMENT FEATURE COMPARISON")
print("=" * 72)

print(f"\nTotal records: {len(df)}")
print(f"Total roads: {df['RoadID'].nunique()}")
print(f"Total Item Codes: {df['Item Code'].nunique()}")

print("\nValidation: Leave-One-Road-Out")
print("Algorithm: Gradient Boosting")
print("Road ID is NOT used as an ML input feature.")


for experiment_name, numeric_features in feature_sets.items():

    print("\n" + "=" * 72)
    print(f"EXPERIMENT: {experiment_name}")
    print("=" * 72)

    print("\nNumeric features:")
    for feature in numeric_features:
        print(f"  - {feature}")

    all_features = (
        numeric_features + categorical_features
    )

    X = df[all_features]

    predictions = np.full(
        shape=len(df),
        fill_value=np.nan,
        dtype=float,
    )

    for train_idx, test_idx in logo.split(
        X, y, groups
    ):

        model = build_model(numeric_features)

        model.fit(
            X.iloc[train_idx],
            y.iloc[train_idx],
        )

        predictions[test_idx] = model.predict(
            X.iloc[test_idx]
        )

        road = groups.iloc[test_idx].iloc[0]

        print(
            f"Completed road {road}: "
            f"{len(test_idx)} test records"
        )

    # Evaluate predictions from all held-out roads.
    mae = mean_absolute_error(
        y, predictions
    )

    rmse = np.sqrt(
        mean_squared_error(y, predictions)
    )

    r2 = r2_score(
        y, predictions
    )

    # Item Code 51 and 69 diagnostics.
    item_51_mask = df["Item Code"] == "51"
    item_69_mask = df["Item Code"] == "69"

    item_51_mae = mean_absolute_error(
        y[item_51_mask],
        predictions[item_51_mask],
    )

    item_69_mae = mean_absolute_error(
        y[item_69_mask],
        predictions[item_69_mask],
    )

    # B0214, Item 69 is our main investigation case.
    b0214_69_mask = (
        (df["RoadID"] == "B0214")
        & (df["Item Code"] == "69")
    )

    if b0214_69_mask.sum() == 1:

        target_index = np.where(
            b0214_69_mask.to_numpy()
        )[0][0]

        b0214_actual = float(
            y.iloc[target_index]
        )

        b0214_prediction = float(
            predictions[target_index]
        )

        b0214_error = abs(
            b0214_actual - b0214_prediction
        )

    else:

        b0214_actual = np.nan
        b0214_prediction = np.nan
        b0214_error = np.nan

    summary_rows.append(
        {
            "Experiment": experiment_name,
            "Overall_MAE_LKR": mae,
            "Overall_RMSE_LKR": rmse,
            "Overall_R2": r2,
            "Item_51_MAE_LKR": item_51_mae,
            "Item_69_MAE_LKR": item_69_mae,
            "B0214_Item_69_Error_LKR": b0214_error,
        }
    )

    experiment_predictions = df[
        [
            "RoadID",
            "Item Code",
            "Units",
            "Length (m)",
            "Width (m)",
            "Calculated_Work_Area_sqm",
            target_column,
        ]
    ].copy()

    experiment_predictions["Experiment"] = (
        experiment_name
    )

    experiment_predictions[
        "ML_Predicted_Cost_LKR"
    ] = predictions

    experiment_predictions[
        "Absolute_Error_LKR"
    ] = np.abs(
        y.to_numpy() - predictions
    )

    prediction_frames.append(
        experiment_predictions
    )

    print("\nResults:")
    print(f"Overall MAE: Rs. {mae:,.2f}")
    print(f"Overall RMSE: Rs. {rmse:,.2f}")
    print(f"Overall R2: {r2:.4f}")

    print(
        f"Item Code 51 MAE: "
        f"Rs. {item_51_mae:,.2f}"
    )

    print(
        f"Item Code 69 MAE: "
        f"Rs. {item_69_mae:,.2f}"
    )

    print(
        f"B0214 Item 69 Error: "
        f"Rs. {b0214_error:,.2f}"
    )

    print(
        f"B0214 Item 69 Prediction: "
        f"Rs. {b0214_prediction:,.2f}"
    )


# --------------------------------------------------
# 6. Compare experiments
# --------------------------------------------------

summary = pd.DataFrame(summary_rows)

summary = summary.sort_values(
    by="Overall_MAE_LKR"
).reset_index(drop=True)

print("\n" + "=" * 72)
print("FINAL FEATURE SET COMPARISON")
print("=" * 72)

print(
    summary.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}",
    )
)


# --------------------------------------------------
# 7. Save results
# --------------------------------------------------

summary_file = (
    OUTPUT_DIR / "measurement_feature_comparison.csv"
)

predictions_file = (
    OUTPUT_DIR / "measurement_feature_predictions.csv"
)

summary.to_csv(
    summary_file,
    index=False,
)

pd.concat(
    prediction_frames,
    ignore_index=True,
).to_csv(
    predictions_file,
    index=False,
)

print("\n" + "=" * 72)
print("SAVED OUTPUT FILES")
print("=" * 72)

print(f"\nSummary: {summary_file}")
print(f"Predictions: {predictions_file}")

print("\nFEATURE COMPARISON COMPLETED!")
