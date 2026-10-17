
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

PREDICTIONS_FILE = (
    PROJECT_DIR
    / "outputs"
    / "nested_tuning_predictions.csv"
)

OUTPUT_DIR = PROJECT_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load saved validation predictions
# --------------------------------------------------

if not PREDICTIONS_FILE.exists():
    raise FileNotFoundError(
        f"Predictions file not found: {PREDICTIONS_FILE}"
    )

df = pd.read_csv(PREDICTIONS_FILE)

required_columns = [
    "RoadID",
    "Item Code",
    "Feature_Set",
    "Model_Type",
    "Repair_Cost_LKR",
    "ML_Predicted_Cost_LKR",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )


# --------------------------------------------------
# 3. Prepare data
# --------------------------------------------------

df["RoadID"] = (
    df["RoadID"].astype(str).str.strip()
)

df["Item Code"] = (
    df["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

for column in [
    "Repair_Cost_LKR",
    "ML_Predicted_Cost_LKR",
]:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )

if df[
    [
        "Repair_Cost_LKR",
        "ML_Predicted_Cost_LKR",
    ]
].isna().any().any():
    raise ValueError(
        "Invalid cost or prediction values found."
    )


# --------------------------------------------------
# 4. Select models for comparison
# --------------------------------------------------

model_options = {
    "A_Baseline": (
        "A_All_Three",
        "Baseline",
    ),
    "A_Nested_Tuned": (
        "A_All_Three",
        "Nested_Tuned",
    ),
    "B_Baseline": (
        "B_Work_Area_Only",
        "Baseline",
    ),
    "B_Nested_Tuned": (
        "B_Work_Area_Only",
        "Nested_Tuned",
    ),
}

selected_frames = []

for model_name, (feature_set, model_type) in (
    model_options.items()
):

    selected = df[
        (df["Feature_Set"] == feature_set)
        & (df["Model_Type"] == model_type)
    ].copy()

    if selected.empty:
        raise ValueError(
            f"No predictions found for {model_name}"
        )

    selected["Model_Name"] = model_name

    selected_frames.append(selected)

comparison_data = pd.concat(
    selected_frames,
    ignore_index=True,
)


# --------------------------------------------------
# 5. Calculate performance by road
# --------------------------------------------------

road_results = []

for (model_name, road_id), group in (
    comparison_data.groupby(
        ["Model_Name", "RoadID"]
    )
):

    actual = group["Repair_Cost_LKR"]
    predicted = group["ML_Predicted_Cost_LKR"]

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

    # R2 is undefined for fewer than 2 records.
    if len(group) >= 2:
        r2 = r2_score(
            actual,
            predicted,
        )
    else:
        r2 = np.nan

    road_results.append(
        {
            "Model": model_name,
            "RoadID": road_id,
            "Record_Count": len(group),
            "MAE_LKR": mae,
            "RMSE_LKR": rmse,
            "R2": r2,
        }
    )

road_summary = pd.DataFrame(road_results)


# --------------------------------------------------
# 6. Create road-by-road MAE comparison
# --------------------------------------------------

mae_table = road_summary.pivot(
    index="RoadID",
    columns="Model",
    values="MAE_LKR",
)

model_order = list(model_options.keys())

mae_table = mae_table[model_order]

mae_table["Best_Model"] = (
    mae_table[model_order].idxmin(axis=1)
)

mae_table["Best_MAE_LKR"] = (
    mae_table[model_order].min(axis=1)
)


# --------------------------------------------------
# 7. Compare Model A and Model B baselines
# --------------------------------------------------

baseline_comparison = mae_table[
    [
        "A_Baseline",
        "B_Baseline",
    ]
].copy()

baseline_comparison["B_MAE_Improvement_LKR"] = (
    baseline_comparison["A_Baseline"]
    - baseline_comparison["B_Baseline"]
)

baseline_comparison["B_Improves_Road"] = (
    baseline_comparison["B_MAE_Improvement_LKR"] > 0
)

improved_road_count = int(
    baseline_comparison["B_Improves_Road"].sum()
)

total_road_count = len(baseline_comparison)


# --------------------------------------------------
# 8. Compare Item Codes 51 and 69 by road
# --------------------------------------------------

item_results = []

for item_code in ["51", "69"]:

    item_data = comparison_data[
        comparison_data["Item Code"] == item_code
    ]

    for (model_name, road_id), group in (
        item_data.groupby(
            ["Model_Name", "RoadID"]
        )
    ):

        mae = mean_absolute_error(
            group["Repair_Cost_LKR"],
            group["ML_Predicted_Cost_LKR"],
        )

        item_results.append(
            {
                "Item_Code": item_code,
                "Model": model_name,
                "RoadID": road_id,
                "Record_Count": len(group),
                "MAE_LKR": mae,
            }
        )

item_summary = pd.DataFrame(item_results)


# --------------------------------------------------
# 9. Print report
# --------------------------------------------------

print("=" * 76)
print("STEP 26 - ROAD-BY-ROAD ML MODEL COMPARISON")
print("=" * 76)

print(f"\nTotal roads: {total_road_count}")
print("Validation predictions: Nested experiment outer folds")

print("\nModels compared:")
for model_name in model_order:
    print(f"  - {model_name}")


print("\n" + "=" * 76)
print("1. MAE COMPARISON BY ROAD")
print("=" * 76)

print(
    mae_table.to_string(
        float_format=lambda value: f"{value:,.2f}"
    )
)


print("\n" + "=" * 76)
print("2. MODEL B VS MODEL A BASELINE")
print("=" * 76)

print(
    baseline_comparison.to_string(
        float_format=lambda value: f"{value:,.2f}"
    )
)

print(
    f"\nModel B improves MAE on "
    f"{improved_road_count} out of "
    f"{total_road_count} roads."
)


print("\n" + "=" * 76)
print("3. ITEM CODE 51 - ERRORS BY ROAD")
print("=" * 76)

item_51 = item_summary[
    item_summary["Item_Code"] == "51"
]

print(
    item_51.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}"
    )
)


print("\n" + "=" * 76)
print("4. ITEM CODE 69 - ERRORS BY ROAD")
print("=" * 76)

item_69 = item_summary[
    item_summary["Item_Code"] == "69"
]

print(
    item_69.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}"
    )
)


# --------------------------------------------------
# 10. Save CSV reports
# --------------------------------------------------

road_file = (
    OUTPUT_DIR / "road_model_comparison.csv"
)

baseline_file = (
    OUTPUT_DIR / "road_baseline_comparison.csv"
)

item_file = (
    OUTPUT_DIR / "item_51_69_road_comparison.csv"
)

road_summary.to_csv(
    road_file,
    index=False,
)

baseline_comparison.reset_index().to_csv(
    baseline_file,
    index=False,
)

item_summary.to_csv(
    item_file,
    index=False,
)


print("\n" + "=" * 76)
print("SAVED REPORTS")
print("=" * 76)

print(f"\nRoad comparison: {road_file}")
print(f"Baseline comparison: {baseline_file}")
print(f"Item comparison: {item_file}")

print("\nROAD-BY-ROAD COMPARISON COMPLETED!")
