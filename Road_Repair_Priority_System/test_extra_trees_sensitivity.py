
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# File paths
# --------------------------------------------------

DATA_FILE = Path("outputs/ml_cost_dataset.csv")
OLD_MODEL_FILE = Path(
    "models/repair_cost_model_without_road_id.joblib"
)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RESULT_FILE = OUTPUT_DIR / "extra_trees_sensitivity.csv"


# --------------------------------------------------
# Load historical dataset
# --------------------------------------------------

df = pd.read_csv(DATA_FILE)

df["Item Code"] = (
    pd.to_numeric(df["Item Code"], errors="coerce")
    .astype("Int64")
    .astype(str)
)

df["Units"] = df["Units"].astype(str).str.strip()

df["Calculated_Work_Area_sqm"] = (
    df["Length (m)"].fillna(0)
    * df["Width (m)"].fillna(0)
)


# --------------------------------------------------
# Extra Trees WITHOUT chainage features
# --------------------------------------------------

NUMERIC_FEATURES = [
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

INPUT_FEATURES = (
    NUMERIC_FEATURES + CATEGORICAL_FEATURES
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            "passthrough",
            NUMERIC_FEATURES,
        ),
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            CATEGORICAL_FEATURES,
        ),
    ]
)

extra_trees_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            ExtraTreesRegressor(
                n_estimators=300,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)


# --------------------------------------------------
# Train candidate on all historical records
# --------------------------------------------------

extra_trees_model.fit(
    df[INPUT_FEATURES],
    df["Repair_Cost_LKR"],
)

print("Extra Trees candidate trained on 123 records.")
print("Existing saved models were NOT changed.")


# --------------------------------------------------
# Load previous Gradient Boosting model
# --------------------------------------------------

old_model = joblib.load(OLD_MODEL_FILE)


# --------------------------------------------------
# Create test scenarios
# --------------------------------------------------

# Keep width fixed and change length to vary area.
WIDTH = 0.225

TEST_AREAS = np.arange(
    22.5,
    112.6,
    1.0,
)

results = []

for work_area in TEST_AREAS:

    length = work_area / WIDTH

    test_input = {
        "StartChainage(m)": 1000,
        "EndChainage(m)": 1100,
        "Depth (m)": 0,
        "Area (sqm)": 0,
        "Count": 0,
        "Times per year (Frequency)": 1,
        "Density (kg/m3)": 0,
        "Length (m)": length,
        "Width (m)": WIDTH,
        "Calculated_Work_Area_sqm": work_area,
        "Item Code": "51",
        "Units": "sq.m",
    }

    test_df = pd.DataFrame([test_input])

    extra_trees_cost = float(
        extra_trees_model.predict(
            test_df[INPUT_FEATURES]
        )[0]
    )

    gb_cost = float(
        old_model.predict(test_df)[0]
    )

    results.append({
        "Work_Area_sqm": work_area,
        "Length_m": length,
        "Width_m": WIDTH,
        "Extra_Trees_Cost_LKR": extra_trees_cost,
        "Gradient_Boosting_Cost_LKR": gb_cost,
    })


# --------------------------------------------------
# Save sensitivity results
# --------------------------------------------------

results_df = pd.DataFrame(results)

results_df.to_csv(
    RESULT_FILE,
    index=False,
)


# --------------------------------------------------
# Analyze prediction behavior
# --------------------------------------------------

print("\n" + "=" * 65)
print("EXTRA TREES SENSITIVITY ANALYSIS")
print("=" * 65)

print("\nRepair Item Code: 51")
print("Units: sq.m")
print("Test Area Range: 22.5 to 112.5 sqm")

for model_column, model_label in [
    ("Extra_Trees_Cost_LKR", "Extra Trees"),
    ("Gradient_Boosting_Cost_LKR", "Gradient Boosting"),
]:

    values = results_df[model_column].to_numpy()

    unique_costs = len(
        np.unique(np.round(values, 2))
    )

    changes = int(
        np.sum(
            ~np.isclose(
                values[1:],
                values[:-1],
                rtol=0,
                atol=0.01,
            )
        )
    )

    print(f"\nMODEL: {model_label}")

    print(f"Unique predicted costs: {unique_costs}")
    print(f"Number of prediction changes: {changes}")

    print(
        f"Minimum prediction: Rs. {values.min():,.2f}"
    )

    print(
        f"Maximum prediction: Rs. {values.max():,.2f}"
    )


# --------------------------------------------------
# Compare selected area examples
# --------------------------------------------------

print("\n" + "=" * 65)
print("SELECTED AREA PREDICTIONS")
print("=" * 65)

for selected_area in [30, 60, 90, 110]:

    nearest_index = (
        results_df["Work_Area_sqm"]
        - selected_area
    ).abs().idxmin()

    record = results_df.loc[nearest_index]

    print(
        f"\nWork Area: "
        f"{record['Work_Area_sqm']:.1f} sqm"
    )

    print(
        f"Extra Trees: "
        f"Rs. {record['Extra_Trees_Cost_LKR']:,.2f}"
    )

    print(
        f"Gradient Boosting: "
        f"Rs. {record['Gradient_Boosting_Cost_LKR']:,.2f}"
    )


print("\n" + "=" * 65)
print("RESULT FILE")
print("=" * 65)

print(RESULT_FILE)

print("\nSensitivity does NOT establish prediction accuracy.")
print("No existing trained model was overwritten.")
