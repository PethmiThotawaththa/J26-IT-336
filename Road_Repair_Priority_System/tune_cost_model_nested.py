
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
# 1. File paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "outputs" / "ml_cost_dataset.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )


# --------------------------------------------------
# 2. Prepare historical data
# --------------------------------------------------

df = pd.read_csv(DATA_FILE)

df["RoadID"] = df["RoadID"].astype(str).str.strip()

df["Item Code"] = (
    df["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

df["Units"] = df["Units"].astype(str).str.strip()

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
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    ).fillna(0)

df["Repair_Cost_LKR"] = pd.to_numeric(
    df["Repair_Cost_LKR"],
    errors="coerce",
)

if df["Repair_Cost_LKR"].isna().any():
    raise ValueError(
        "Missing or invalid repair cost values found."
    )

df["Calculated_Work_Area_sqm"] = (
    df["Length (m)"] * df["Width (m)"]
)


# --------------------------------------------------
# 3. Feature sets
# --------------------------------------------------

common_numeric = [
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
    "A_All_Three": (
        common_numeric
        + [
            "Length (m)",
            "Width (m)",
            "Calculated_Work_Area_sqm",
        ]
    ),
    "B_Work_Area_Only": (
        common_numeric
        + [
            "Calculated_Work_Area_sqm",
        ]
    ),
}


# --------------------------------------------------
# 4. Hyperparameter candidates
# --------------------------------------------------

# These are deliberately limited to keep the
# experiment manageable on a small dataset.

candidates = [
    {
        "name": "Baseline",
        "n_estimators": 200,
        "learning_rate": 0.05,
        "max_depth": 3,
        "min_samples_leaf": 1,
    },
    {
        "name": "T1",
        "n_estimators": 100,
        "learning_rate": 0.05,
        "max_depth": 2,
        "min_samples_leaf": 2,
    },
    {
        "name": "T2",
        "n_estimators": 200,
        "learning_rate": 0.05,
        "max_depth": 2,
        "min_samples_leaf": 2,
    },
    {
        "name": "T3",
        "n_estimators": 300,
        "learning_rate": 0.03,
        "max_depth": 2,
        "min_samples_leaf": 2,
    },
    {
        "name": "T4",
        "n_estimators": 200,
        "learning_rate": 0.05,
        "max_depth": 3,
        "min_samples_leaf": 3,
    },
    {
        "name": "T5",
        "n_estimators": 300,
        "learning_rate": 0.03,
        "max_depth": 3,
        "min_samples_leaf": 4,
    },
]


# --------------------------------------------------
# 5. Model builder
# --------------------------------------------------

def build_model(numeric_features, settings):

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
        n_estimators=settings["n_estimators"],
        learning_rate=settings["learning_rate"],
        max_depth=settings["max_depth"],
        min_samples_leaf=settings["min_samples_leaf"],
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", regressor),
        ]
    )


# --------------------------------------------------
# 6. Inner validation for hyperparameter selection
# --------------------------------------------------

def select_best_settings(
    X_train,
    y_train,
    road_groups,
    numeric_features,
):

    inner_logo = LeaveOneGroupOut()

    candidate_results = []

    for settings in candidates:

        inner_predictions = np.full(
            len(X_train),
            np.nan,
            dtype=float,
        )

        for inner_train_idx, inner_test_idx in (
            inner_logo.split(
                X_train,
                y_train,
                road_groups,
            )
        ):

            model = build_model(
                numeric_features,
                settings,
            )

            model.fit(
                X_train.iloc[inner_train_idx],
                y_train.iloc[inner_train_idx],
            )

            inner_predictions[inner_test_idx] = (
                model.predict(
                    X_train.iloc[inner_test_idx]
                )
            )

        inner_mae = mean_absolute_error(
            y_train,
            inner_predictions,
        )

        candidate_results.append(
            {
                "settings": settings,
                "inner_mae": inner_mae,
            }
        )

    best = min(
        candidate_results,
        key=lambda result: result["inner_mae"],
    )

    return best["settings"], best["inner_mae"]


# --------------------------------------------------
# 7. Nested Leave-One-Road-Out evaluation
# --------------------------------------------------

outer_logo = LeaveOneGroupOut()

y = df["Repair_Cost_LKR"]
groups = df["RoadID"]

summary_rows = []
fold_rows = []
prediction_frames = []


print("=" * 76)
print("STEP 25 - NESTED ML HYPERPARAMETER TUNING")
print("=" * 76)

print(f"\nTotal records: {len(df)}")
print(f"Total roads: {groups.nunique()}")
print(f"Total Item Codes: {df['Item Code'].nunique()}")

print("\nAlgorithm: Gradient Boosting")
print("Outer validation: Leave-One-Road-Out")
print("Inner tuning: Leave-One-Road-Out")
print(f"Hyperparameter candidates: {len(candidates)}")
print("Road ID is not used as an ML feature.")

print(
    "\nNote: This experiment may take several minutes."
)


for feature_name, numeric_features in feature_sets.items():

    print("\n" + "=" * 76)
    print(f"FEATURE SET: {feature_name}")
    print("=" * 76)

    all_features = (
        numeric_features + categorical_features
    )

    X = df[all_features]

    baseline_predictions = np.full(
        len(df),
        np.nan,
        dtype=float,
    )

    tuned_predictions = np.full(
        len(df),
        np.nan,
        dtype=float,
    )

    for outer_train_idx, outer_test_idx in (
        outer_logo.split(X, y, groups)
    ):

        X_train = X.iloc[outer_train_idx]
        X_test = X.iloc[outer_test_idx]

        y_train = y.iloc[outer_train_idx]
        y_test = y.iloc[outer_test_idx]

        train_groups = groups.iloc[outer_train_idx]

        test_road = groups.iloc[outer_test_idx].iloc[0]

        # Train the unchanged baseline model.
        baseline_model = build_model(
            numeric_features,
            candidates[0],
        )

        baseline_model.fit(
            X_train,
            y_train,
        )

        baseline_fold_predictions = (
            baseline_model.predict(X_test)
        )

        baseline_predictions[outer_test_idx] = (
            baseline_fold_predictions
        )

        # Select settings using only training roads.
        best_settings, inner_mae = (
            select_best_settings(
                X_train,
                y_train,
                train_groups,
                numeric_features,
            )
        )

        # Retrain using all outer training records.
        tuned_model = build_model(
            numeric_features,
            best_settings,
        )

        tuned_model.fit(
            X_train,
            y_train,
        )

        tuned_fold_predictions = (
            tuned_model.predict(X_test)
        )

        tuned_predictions[outer_test_idx] = (
            tuned_fold_predictions
        )

        baseline_fold_mae = mean_absolute_error(
            y_test,
            baseline_fold_predictions,
        )

        tuned_fold_mae = mean_absolute_error(
            y_test,
            tuned_fold_predictions,
        )

        fold_rows.append(
            {
                "Feature_Set": feature_name,
                "Test_Road": test_road,
                "Test_Records": len(outer_test_idx),
                "Selected_Candidate": best_settings["name"],
                "Inner_MAE_LKR": inner_mae,
                "Baseline_Outer_MAE_LKR": baseline_fold_mae,
                "Tuned_Outer_MAE_LKR": tuned_fold_mae,
            }
        )

        print(
            f"\nTest road: {test_road}"
        )

        print(
            f"  Selected settings: "
            f"{best_settings['name']}"
        )

        print(
            f"  Inner validation MAE: "
            f"Rs. {inner_mae:,.2f}"
        )

        print(
            f"  Baseline test MAE: "
            f"Rs. {baseline_fold_mae:,.2f}"
        )

        print(
            f"  Tuned test MAE: "
            f"Rs. {tuned_fold_mae:,.2f}"
        )

    # Evaluate both approaches using the same outer folds.
    for model_type, predictions in [
        ("Baseline", baseline_predictions),
        ("Nested_Tuned", tuned_predictions),
    ]:

        overall_mae = mean_absolute_error(
            y,
            predictions,
        )

        overall_rmse = np.sqrt(
            mean_squared_error(
                y,
                predictions,
            )
        )

        overall_r2 = r2_score(
            y,
            predictions,
        )

        item_51_mask = (
            df["Item Code"] == "51"
        )

        item_69_mask = (
            df["Item Code"] == "69"
        )

        item_51_mae = mean_absolute_error(
            y[item_51_mask],
            predictions[item_51_mask],
        )

        item_69_mae = mean_absolute_error(
            y[item_69_mask],
            predictions[item_69_mask],
        )

        b0214_69_mask = (
            (df["RoadID"] == "B0214")
            & (df["Item Code"] == "69")
        )

        if b0214_69_mask.sum() == 1:

            target_index = np.where(
                b0214_69_mask.to_numpy()
            )[0][0]

            b0214_error = abs(
                float(y.iloc[target_index])
                - float(predictions[target_index])
            )

        else:
            b0214_error = np.nan

        summary_rows.append(
            {
                "Feature_Set": feature_name,
                "Model_Type": model_type,
                "Overall_MAE_LKR": overall_mae,
                "Overall_RMSE_LKR": overall_rmse,
                "Overall_R2": overall_r2,
                "Item_51_MAE_LKR": item_51_mae,
                "Item_69_MAE_LKR": item_69_mae,
                "B0214_Item_69_Error_LKR": b0214_error,
            }
        )

        prediction_frame = df[
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

        prediction_frame["Feature_Set"] = feature_name
        prediction_frame["Model_Type"] = model_type

        prediction_frame[
            "ML_Predicted_Cost_LKR"
        ] = predictions

        prediction_frame[
            "Absolute_Error_LKR"
        ] = np.abs(
            y.to_numpy() - predictions
        )

        prediction_frames.append(
            prediction_frame
        )


# --------------------------------------------------
# 8. Print final comparison
# --------------------------------------------------

summary = pd.DataFrame(summary_rows)

summary = summary.sort_values(
    by="Overall_MAE_LKR"
).reset_index(drop=True)

fold_details = pd.DataFrame(fold_rows)

print("\n" + "=" * 76)
print("FINAL NESTED VALIDATION RESULTS")
print("=" * 76)

print(
    summary.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}",
    )
)

print("\n" + "=" * 76)
print("SELECTED SETTINGS BY TEST ROAD")
print("=" * 76)

print(
    fold_details.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}",
    )
)


# --------------------------------------------------
# 9. Save reports
# --------------------------------------------------

summary_file = (
    OUTPUT_DIR / "nested_tuning_summary.csv"
)

fold_file = (
    OUTPUT_DIR / "nested_tuning_road_details.csv"
)

predictions_file = (
    OUTPUT_DIR / "nested_tuning_predictions.csv"
)

summary.to_csv(
    summary_file,
    index=False,
)

fold_details.to_csv(
    fold_file,
    index=False,
)

pd.concat(
    prediction_frames,
    ignore_index=True,
).to_csv(
    predictions_file,
    index=False,
)

print("\n" + "=" * 76)
print("SAVED REPORTS")
print("=" * 76)

print(f"\nSummary: {summary_file}")
print(f"Road details: {fold_file}")
print(f"Predictions: {predictions_file}")

print("\nNESTED TUNING EXPERIMENT COMPLETED!")
