
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingRegressor,
    ExtraTreesRegressor,
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# File paths
# --------------------------------------------------

DATA_FILE = Path("outputs/ml_cost_dataset.csv")

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_FILE = (
    OUTPUT_DIR / "chainage_feature_comparison.csv"
)

PREDICTIONS_FILE = (
    OUTPUT_DIR / "chainage_feature_predictions.csv"
)


# --------------------------------------------------
# Load historical repair dataset
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
    pd.to_numeric(
        df["Item Code"],
        errors="coerce",
    )
    .astype("Int64")
    .astype(str)
)

df["Units"] = (
    df["Units"].astype(str).str.strip()
)

df["Calculated_Work_Area_sqm"] = (
    df["Length (m)"].fillna(0)
    * df["Width (m)"].fillna(0)
)


# --------------------------------------------------
# Define target and input features
# --------------------------------------------------

TARGET_COLUMN = "Repair_Cost_LKR"

CHAINAGE_FEATURES = [
    "StartChainage(m)",
    "EndChainage(m)",
]

OTHER_NUMERIC_FEATURES = [
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Length (m)",
    "Width (m)",
    "Calculated_Work_Area_sqm",
]

CATEGORICAL_FEATURES = [
    "Item Code",
    "Units",
]

FEATURE_SETS = {
    "With_Chainage": (
        CHAINAGE_FEATURES
        + OTHER_NUMERIC_FEATURES
    ),

    "Without_Chainage": (
        OTHER_NUMERIC_FEATURES
    ),
}


# --------------------------------------------------
# Build machine learning models
# --------------------------------------------------

def create_ml_model(model_name, numeric_features):

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
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    if model_name == "Gradient_Boosting":

        estimator = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        )

    elif model_name == "Extra_Trees":

        estimator = ExtraTreesRegressor(
            n_estimators=300,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
        )

    else:

        raise ValueError(
            f"Unknown model: {model_name}"
        )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", estimator),
        ]
    )


# --------------------------------------------------
# Leave-One-Road-Out validation
# --------------------------------------------------

prediction_rows = []

road_ids = sorted(
    df["RoadID"].unique()
)

MODEL_NAMES = [
    "Gradient_Boosting",
    "Extra_Trees",
]

for model_name in MODEL_NAMES:

    for feature_set_name, numeric_features in (
        FEATURE_SETS.items()
    ):

        print(
            f"\nTesting: {model_name} | "
            f"{feature_set_name}"
        )

        input_features = (
            numeric_features
            + CATEGORICAL_FEATURES
        )

        for test_road in road_ids:

            training_data = df[
                df["RoadID"] != test_road
            ].copy()

            testing_data = df[
                df["RoadID"] == test_road
            ].copy()

            ml_model = create_ml_model(
                model_name,
                numeric_features,
            )

            ml_model.fit(
                training_data[input_features],
                training_data[TARGET_COLUMN],
            )

            predicted_values = ml_model.predict(
                testing_data[input_features]
            )

            for position, (row_index, record) in enumerate(
                testing_data.iterrows()
            ):

                actual_cost = float(
                    record[TARGET_COLUMN]
                )

                predicted_cost = float(
                    predicted_values[position]
                )

                prediction_rows.append({
                    "Model": model_name,
                    "Feature_Set": feature_set_name,
                    "Original_Row_Index": row_index,
                    "RoadID": record["RoadID"],
                    "Item_Code": record["Item Code"],
                    "Units": record["Units"],
                    "Length_m": record["Length (m)"],
                    "Width_m": record["Width (m)"],
                    "Work_Area_sqm": record[
                        "Calculated_Work_Area_sqm"
                    ],
                    "Actual_Cost_LKR": actual_cost,
                    "Predicted_Cost_LKR": predicted_cost,
                    "Absolute_Error_LKR": abs(
                        actual_cost - predicted_cost
                    ),
                })


# --------------------------------------------------
# Create prediction results table
# --------------------------------------------------

results_predictions_df = pd.DataFrame(
    prediction_rows
)


# --------------------------------------------------
# Calculate validation metrics
# --------------------------------------------------

def calculate_metrics(group_data):

    if group_data.empty:

        return {
            "Records": 0,
            "MAE_LKR": np.nan,
            "RMSE_LKR": np.nan,
        }

    actual_values = group_data[
        "Actual_Cost_LKR"
    ].to_numpy()

    predicted_values = group_data[
        "Predicted_Cost_LKR"
    ].to_numpy()

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

    return {
        "Records": len(group_data),
        "MAE_LKR": mae,
        "RMSE_LKR": rmse,
    }


# --------------------------------------------------
# Evaluate overall and small-area accuracy
# --------------------------------------------------

metric_rows = []

for (model_name, feature_set_name), model_results in (
    results_predictions_df.groupby(
        ["Model", "Feature_Set"]
    )
):

    small_area_mask = (
        (model_results["Work_Area_sqm"] > 0)
        & (model_results["Work_Area_sqm"] <= 200)
        & (model_results["Units"] == "sq.m")
    )

    evaluation_groups = {
        "Overall": model_results,

        "Small_Area": model_results[
            small_area_mask
        ],

        "Item_51": model_results[
            small_area_mask
            & (
                model_results["Item_Code"]
                == "51"
            )
        ],

        "Other_Small_Items": model_results[
            small_area_mask
            & (
                model_results["Item_Code"]
                != "51"
            )
        ],
    }

    for group_name, group_data in (
        evaluation_groups.items()
    ):

        metrics = calculate_metrics(
            group_data
        )

        metric_rows.append({
            "Model": model_name,
            "Feature_Set": feature_set_name,
            "Group": group_name,
            **metrics,
        })


# --------------------------------------------------
# Create and save final reports
# --------------------------------------------------

results_metrics_df = pd.DataFrame(
    metric_rows
)

results_metrics_df.to_csv(
    SUMMARY_FILE,
    index=False,
)

results_predictions_df.to_csv(
    PREDICTIONS_FILE,
    index=False,
)


# --------------------------------------------------
# Print readable report
# --------------------------------------------------

print("\n" + "=" * 75)
print("CHAINAGE FEATURE COMPARISON RESULTS")
print("=" * 75)

GROUP_NAMES = [
    "Overall",
    "Small_Area",
    "Item_51",
    "Other_Small_Items",
]

for group_name in GROUP_NAMES:

    print(
        f"\nGROUP: {group_name}"
    )

    selected_results = results_metrics_df[
        results_metrics_df["Group"]
        == group_name
    ].sort_values(
        "MAE_LKR"
    )

    for _, result_row in selected_results.iterrows():

        print(
            f"{result_row['Model']:20s} | "
            f"{result_row['Feature_Set']:17s} | "
            f"Records: {int(result_row['Records']):3d} | "
            f"MAE: Rs. {result_row['MAE_LKR']:,.2f}"
        )


# --------------------------------------------------
# Inspect Item Code 51, 72 sqm case
# --------------------------------------------------

print("\n" + "=" * 75)
print("ITEM CODE 51 - 72 SQM CASE")
print("=" * 75)

case_results = results_predictions_df[
    (results_predictions_df["Item_Code"] == "51")
    & (
        np.isclose(
            results_predictions_df["Work_Area_sqm"],
            72.0,
        )
    )
]

if case_results.empty:

    print("No matching 72 sqm record found.")

else:

    for _, result_row in case_results.iterrows():

        print(
            f"{result_row['Model']:20s} | "
            f"{result_row['Feature_Set']:17s} | "
            f"Actual: Rs. "
            f"{result_row['Actual_Cost_LKR']:,.2f} | "
            f"Predicted: Rs. "
            f"{result_row['Predicted_Cost_LKR']:,.2f} | "
            f"Error: Rs. "
            f"{result_row['Absolute_Error_LKR']:,.2f}"
        )


# --------------------------------------------------
# Completion message
# --------------------------------------------------

print("\n" + "=" * 75)
print("REPORT FILES SAVED")
print("=" * 75)

print(SUMMARY_FILE)
print(PREDICTIONS_FILE)

print(
    "\nExisting trained ML models were NOT modified."
)
