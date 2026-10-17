
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# --------------------------------------------------
# File paths
# --------------------------------------------------

DATA_FILE = Path("outputs/ml_cost_dataset.csv")

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_FILE = (
    OUTPUT_DIR / "small_area_model_comparison.csv"
)

PREDICTIONS_FILE = (
    OUTPUT_DIR / "small_area_model_predictions.csv"
)


# --------------------------------------------------
# Load dataset
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
# Define features
# --------------------------------------------------

TARGET_COLUMN = "Repair_Cost_LKR"

COMMON_NUMERIC_FEATURES = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
]

FEATURE_SETS = {
    "All_Three": COMMON_NUMERIC_FEATURES + [
        "Length (m)",
        "Width (m)",
        "Calculated_Work_Area_sqm",
    ],

    "Work_Area_Only": COMMON_NUMERIC_FEATURES + [
        "Calculated_Work_Area_sqm",
    ],
}

CATEGORICAL_FEATURES = [
    "Item Code",
    "Units",
]


# --------------------------------------------------
# Create ML models
# --------------------------------------------------

def create_model(model_name, numeric_features):

    if model_name in [
        "GB_A",
        "GB_Work_Area_Only",
    ]:

        estimator = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        )

        numeric_transformer = "passthrough"

    elif model_name == "Extra_Trees":

        estimator = ExtraTreesRegressor(
            n_estimators=300,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
        )

        numeric_transformer = "passthrough"

    elif model_name == "Random_Forest":

        estimator = RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
        )

        numeric_transformer = "passthrough"

    elif model_name == "Ridge":

        estimator = Ridge(
            alpha=10.0
        )

        numeric_transformer = StandardScaler()

    else:

        raise ValueError(
            f"Unknown model: {model_name}"
        )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_transformer,
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

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", estimator),
        ]
    )


# --------------------------------------------------
# Model configurations
# --------------------------------------------------

MODEL_CONFIGURATIONS = [
    ("GB_A", "All_Three"),
    ("GB_Work_Area_Only", "Work_Area_Only"),
    ("Extra_Trees", "All_Three"),
    ("Random_Forest", "All_Three"),
    ("Ridge", "All_Three"),
]


# --------------------------------------------------
# Calculate accuracy metrics
# --------------------------------------------------

def calculate_metrics(actual_values, predicted_values):

    if len(actual_values) == 0:

        return {
            "Records": 0,
            "MAE_LKR": np.nan,
            "RMSE_LKR": np.nan,
            "R2": np.nan,
            "Relative_MAE_Percent": np.nan,
        }

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

    if len(actual_values) >= 2:

        r2 = r2_score(
            actual_values,
            predicted_values,
        )

    else:

        r2 = np.nan

    average_actual_cost = np.mean(
        actual_values
    )

    if average_actual_cost > 0:

        relative_mae = (
            mae / average_actual_cost
        ) * 100

    else:

        relative_mae = np.nan

    return {
        "Records": len(actual_values),
        "MAE_LKR": mae,
        "RMSE_LKR": rmse,
        "R2": r2,
        "Relative_MAE_Percent": relative_mae,
    }


# --------------------------------------------------
# Leave-One-Road-Out validation
# --------------------------------------------------

all_prediction_tables = []
all_metric_rows = []

road_ids = sorted(
    df["RoadID"].unique()
)

for model_name, feature_set_name in (
    MODEL_CONFIGURATIONS
):

    print(
        f"\nEvaluating: {model_name}"
    )

    numeric_features = FEATURE_SETS[
        feature_set_name
    ]

    input_features = (
        numeric_features
        + CATEGORICAL_FEATURES
    )

    prediction_rows = []

    for test_road in road_ids:

        training_data = df[
            df["RoadID"] != test_road
        ].copy()

        testing_data = df[
            df["RoadID"] == test_road
        ].copy()

        ml_model = create_model(
            model_name,
            numeric_features,
        )

        ml_model.fit(
            training_data[input_features],
            training_data[TARGET_COLUMN],
        )

        predictions = ml_model.predict(
            testing_data[input_features]
        )

        for position, (row_index, record) in enumerate(
            testing_data.iterrows()
        ):

            actual_cost = float(
                record[TARGET_COLUMN]
            )

            predicted_cost = float(
                predictions[position]
            )

            prediction_rows.append({
                "Model": model_name,
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

    model_predictions_df = pd.DataFrame(
        prediction_rows
    )

    all_prediction_tables.append(
        model_predictions_df
    )

    # Identify small area-based repairs.
    small_area_mask = (
        (model_predictions_df["Work_Area_sqm"] > 0)
        & (model_predictions_df["Work_Area_sqm"] <= 200)
        & (model_predictions_df["Units"] == "sq.m")
    )

    evaluation_groups = {
        "Overall_All_Records": model_predictions_df,

        "Small_Area_0_to_200_sqm":
            model_predictions_df[
                small_area_mask
            ],

        "Small_Area_Item_51":
            model_predictions_df[
                small_area_mask
                & (
                    model_predictions_df["Item_Code"]
                    == "51"
                )
            ],

        "Small_Area_Other_Items":
            model_predictions_df[
                small_area_mask
                & (
                    model_predictions_df["Item_Code"]
                    != "51"
                )
            ],
    }

    for group_name, group_data in (
        evaluation_groups.items()
    ):

        metric_values = calculate_metrics(
            group_data[
                "Actual_Cost_LKR"
            ].to_numpy(),

            group_data[
                "Predicted_Cost_LKR"
            ].to_numpy(),
        )

        all_metric_rows.append({
            "Model": model_name,
            "Group": group_name,
            **metric_values,
        })


# --------------------------------------------------
# Create final report DataFrames
# --------------------------------------------------

results_summary_df = pd.DataFrame(
    all_metric_rows
)

results_predictions_df = pd.concat(
    all_prediction_tables,
    ignore_index=True,
)


# --------------------------------------------------
# Save CSV reports
# --------------------------------------------------

results_summary_df.to_csv(
    SUMMARY_FILE,
    index=False,
)

results_predictions_df.to_csv(
    PREDICTIONS_FILE,
    index=False,
)


# --------------------------------------------------
# Print comparison report
# --------------------------------------------------

print("\n" + "=" * 65)
print("SMALL-AREA ML MODEL COMPARISON")
print("=" * 65)

evaluation_group_names = [
    "Overall_All_Records",
    "Small_Area_0_to_200_sqm",
    "Small_Area_Item_51",
    "Small_Area_Other_Items",
]

for group_name in evaluation_group_names:

    print(
        f"\nGROUP: {group_name}"
    )

    selected_results = results_summary_df[
        results_summary_df["Group"] == group_name
    ].sort_values(
        "MAE_LKR"
    )

    for _, result_row in selected_results.iterrows():

        print(
            f"{result_row['Model']:20s} | "
            f"Records: {int(result_row['Records']):3d} | "
            f"MAE: Rs. {result_row['MAE_LKR']:,.2f} | "
            f"Relative MAE: "
            f"{result_row['Relative_MAE_Percent']:.2f}%"
        )


# --------------------------------------------------
# Completion message
# --------------------------------------------------

print("\n" + "=" * 65)
print("REPORT FILES SAVED")
print("=" * 65)

print(SUMMARY_FILE)
print(PREDICTIONS_FILE)

print(
    "\nExisting trained ML models were NOT modified."
)

print(
    "Model selection requires further validation."
)
