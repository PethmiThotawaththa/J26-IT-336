
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
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
# 1. Project paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    PROJECT_DIR
    / "outputs"
    / "ml_cost_dataset.csv"
)

OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load historical dataset
# --------------------------------------------------

data = pd.read_csv(DATA_FILE)

data["RoadID"] = (
    data["RoadID"]
    .astype(str)
    .str.strip()
)

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

numeric_features = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Length (m)",
    "Width (m)",
    "Calculated_Work_Area_sqm",
]

categorical_features = [
    "Item Code",
    "Units",
]

for column in numeric_features:

    if column == "Calculated_Work_Area_sqm":
        continue

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce",
    ).fillna(0.0)

data["Calculated_Work_Area_sqm"] = (
    data["Length (m)"]
    * data["Width (m)"]
)

data["Repair_Cost_LKR"] = pd.to_numeric(
    data["Repair_Cost_LKR"],
    errors="coerce",
)

data = data.dropna(
    subset=["Repair_Cost_LKR"]
).copy()

features = numeric_features + categorical_features

road_ids = sorted(
    data["RoadID"].unique()
)


# --------------------------------------------------
# 3. Define machine learning models
# --------------------------------------------------

def build_gradient_boosting():

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

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                GradientBoostingRegressor(
                    n_estimators=200,
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=42,
                ),
            ),
        ]
    )


def build_rbf_svr():

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
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

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                SVR(
                    kernel="rbf",
                    C=100000.0,
                    epsilon=10000.0,
                    gamma="scale",
                ),
            ),
        ]
    )


model_builders = {
    "Gradient_Boosting_A": build_gradient_boosting,
    "RBF_SVR": build_rbf_svr,
}


# --------------------------------------------------
# 4. Leave-One-Road-Out validation
# --------------------------------------------------

prediction_rows = []

for model_name, model_builder in model_builders.items():

    print("\n" + "=" * 65)
    print(f"VALIDATING: {model_name}")
    print("=" * 65)

    for test_road in road_ids:

        train_data = data[
            data["RoadID"] != test_road
        ]

        test_data = data[
            data["RoadID"] == test_road
        ]

        X_train = train_data[features]
        y_train = train_data["Repair_Cost_LKR"]

        X_test = test_data[features]
        y_test = test_data["Repair_Cost_LKR"]

        model = model_builder()

        model.fit(
            X_train,
            y_train,
        )

        predictions = model.predict(X_test)

        road_mae = mean_absolute_error(
            y_test,
            predictions,
        )

        print(
            f"{test_road}: "
            f"Records={len(test_data)}, "
            f"MAE=Rs. {road_mae:,.2f}"
        )

        for index, prediction in zip(
            test_data.index,
            predictions,
        ):

            actual = float(
                data.loc[
                    index,
                    "Repair_Cost_LKR",
                ]
            )

            prediction_rows.append(
                {
                    "Model": model_name,
                    "RoadID": test_road,
                    "Item Code": data.loc[
                        index,
                        "Item Code",
                    ],
                    "Actual_Cost_LKR": actual,
                    "Predicted_Cost_LKR": float(
                        prediction
                    ),
                    "Absolute_Error_LKR": abs(
                        actual - prediction
                    ),
                }
            )


predictions_df = pd.DataFrame(
    prediction_rows
)


# --------------------------------------------------
# 5. Overall and item-code accuracy
# --------------------------------------------------

summary_rows = []

for model_name in model_builders:

    model_results = predictions_df[
        predictions_df["Model"] == model_name
    ]

    actual = model_results["Actual_Cost_LKR"]
    predicted = model_results["Predicted_Cost_LKR"]

    summary = {
        "Model": model_name,
        "Overall_MAE_LKR": mean_absolute_error(
            actual,
            predicted,
        ),
        "Overall_RMSE_LKR": np.sqrt(
            mean_squared_error(
                actual,
                predicted,
            )
        ),
        "Overall_R2": r2_score(
            actual,
            predicted,
        ),
    }

    for item_code in ["51", "69"]:

        item_results = model_results[
            model_results["Item Code"] == item_code
        ]

        if not item_results.empty:

            summary[
                f"Item_{item_code}_MAE_LKR"
            ] = mean_absolute_error(
                item_results["Actual_Cost_LKR"],
                item_results["Predicted_Cost_LKR"],
            )

    summary_rows.append(summary)


summary_df = pd.DataFrame(
    summary_rows
)

summary_df = summary_df.sort_values(
    "Overall_MAE_LKR"
)


# --------------------------------------------------
# 6. Work-area sensitivity test
# --------------------------------------------------

sensitivity_rows = []

test_areas = np.linspace(
    22.5,
    112.5,
    91,
)

for model_name, model_builder in model_builders.items():

    model = model_builder()

    model.fit(
        data[features],
        data["Repair_Cost_LKR"],
    )

    for work_area in test_areas:

        width = 0.3
        length = work_area / width

        scenario = pd.DataFrame(
            [
                {
                    "StartChainage(m)": 1000.0,
                    "EndChainage(m)": 1100.0,
                    "Depth (m)": 0.0,
                    "Area (sqm)": 0.0,
                    "Count": 0.0,
                    "Times per year (Frequency)": 1.0,
                    "Density (kg/m3)": 0.0,
                    "Length (m)": length,
                    "Width (m)": width,
                    "Calculated_Work_Area_sqm": work_area,
                    "Item Code": "51",
                    "Units": "sq.m",
                }
            ]
        )

        prediction = float(
            model.predict(
                scenario[features]
            )[0]
        )

        sensitivity_rows.append(
            {
                "Model": model_name,
                "Item Code": "51",
                "Work_Area_sqm": work_area,
                "Predicted_Cost_LKR": prediction,
            }
        )


sensitivity_df = pd.DataFrame(
    sensitivity_rows
)


# --------------------------------------------------
# 7. Sensitivity statistics
# --------------------------------------------------

sensitivity_summary_rows = []

for model_name in model_builders:

    model_results = sensitivity_df[
        sensitivity_df["Model"] == model_name
    ].sort_values(
        "Work_Area_sqm"
    )

    costs = model_results[
        "Predicted_Cost_LKR"
    ].to_numpy()

    changes = np.diff(costs)

    sensitivity_summary_rows.append(
        {
            "Model": model_name,
            "Unique_Predicted_Costs": len(
                np.unique(
                    np.round(costs, 2)
                )
            ),
            "Prediction_Change_Count": int(
                np.sum(
                    np.abs(changes) > 0.01
                )
            ),
            "Minimum_Cost_LKR": float(
                np.min(costs)
            ),
            "Maximum_Cost_LKR": float(
                np.max(costs)
            ),
            "Negative_Prediction_Count": int(
                np.sum(costs < 0)
            ),
        }
    )


sensitivity_summary_df = pd.DataFrame(
    sensitivity_summary_rows
)


# --------------------------------------------------
# 8. Print comparison report
# --------------------------------------------------

print("\n" + "=" * 65)
print("STEP 30 - GRADIENT BOOSTING VS RBF-SVR")
print("=" * 65)

print("\nHistorical records:", len(data))
print("Roads:", len(road_ids))
print("Validation: Leave-One-Road-Out")

print("\nOVERALL AND ITEM-CODE ACCURACY")

print(
    summary_df.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}",
    )
)

print("\nSENSITIVITY SUMMARY - ITEM CODE 51")

print(
    sensitivity_summary_df.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}",
    )
)

print("\nSELECTED WORK-AREA PREDICTIONS")

selected_areas = [
    30.5,
    60.5,
    90.5,
    105.5,
]

selected_results = sensitivity_df[
    sensitivity_df["Work_Area_sqm"].isin(
        selected_areas
    )
]

print(
    selected_results.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}",
    )
)

print("\nLowest overall MAE:")
print(
    summary_df.iloc[0]["Model"]
)

print(
    "\nNote: SVR parameters are initial experimental "
    "settings, not tuned optimal values."
)

print(
    "Smooth predictions do not guarantee "
    "accurate repair cost estimates."
)


# --------------------------------------------------
# 9. Save reports
# --------------------------------------------------

summary_file = (
    OUTPUT_DIR
    / "svr_comparison_summary.csv"
)

predictions_file = (
    OUTPUT_DIR
    / "svr_comparison_predictions.csv"
)

sensitivity_file = (
    OUTPUT_DIR
    / "svr_sensitivity_predictions.csv"
)

sensitivity_summary_file = (
    OUTPUT_DIR
    / "svr_sensitivity_summary.csv"
)

summary_df.to_csv(
    summary_file,
    index=False,
)

predictions_df.to_csv(
    predictions_file,
    index=False,
)

sensitivity_df.to_csv(
    sensitivity_file,
    index=False,
)

sensitivity_summary_df.to_csv(
    sensitivity_summary_file,
    index=False,
)

print("\nSaved files:")
print(summary_file)
print(predictions_file)
print(sensitivity_file)
print(sensitivity_summary_file)

print("\nSTEP 30 COMPLETED!")
