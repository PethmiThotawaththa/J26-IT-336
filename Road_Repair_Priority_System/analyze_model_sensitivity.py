
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

MODEL_FILE = (
    PROJECT_DIR
    / "models"
    / "repair_cost_model_without_road_id.joblib"
)

DATA_FILE = (
    PROJECT_DIR
    / "outputs"
    / "ml_cost_dataset.csv"
)

OUTPUT_DIR = PROJECT_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load trained model and historical data
# --------------------------------------------------

if not MODEL_FILE.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_FILE}"
    )

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )

model = joblib.load(MODEL_FILE)
historical_data = pd.read_csv(DATA_FILE)

historical_data["Item Code"] = (
    historical_data["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

historical_data["Units"] = (
    historical_data["Units"]
    .astype(str)
    .str.strip()
)


# --------------------------------------------------
# 3. Select Item Code 51
# --------------------------------------------------

ITEM_CODE = "51"

item_records = historical_data[
    historical_data["Item Code"] == ITEM_CODE
].copy()

if item_records.empty:
    raise ValueError(
        "Item Code 51 not found in historical data."
    )

item_records["Length (m)"] = pd.to_numeric(
    item_records["Length (m)"],
    errors="coerce",
).fillna(0)

item_records["Width (m)"] = pd.to_numeric(
    item_records["Width (m)"],
    errors="coerce",
).fillna(0)

item_records["Calculated_Work_Area_sqm"] = (
    item_records["Length (m)"]
    * item_records["Width (m)"]
)

positive_areas = item_records.loc[
    item_records["Calculated_Work_Area_sqm"] > 0,
    "Calculated_Work_Area_sqm",
]

if positive_areas.empty:
    raise ValueError(
        "No positive historical work areas found."
    )

minimum_area = float(positive_areas.min())
maximum_area = float(positive_areas.max())


# --------------------------------------------------
# 4. Create test scenarios
# --------------------------------------------------

# Keep all other inputs identical to the manual tests.
# Change only Length and Calculated Work Area.
# Width remains 0.3 m.

FIXED_WIDTH = 0.3

test_areas = np.linspace(
    minimum_area,
    maximum_area,
    91,
)

scenario_rows = []

for work_area in test_areas:

    length = work_area / FIXED_WIDTH

    scenario_rows.append(
        {
            "StartChainage(m)": 1000.0,
            "EndChainage(m)": 1100.0,
            "Length (m)": length,
            "Width (m)": FIXED_WIDTH,
            "Depth (m)": 0.0,
            "Area (sqm)": 0.0,
            "Count": 0.0,
            "Times per year (Frequency)": 1.0,
            "Density (kg/m3)": 0.0,
            "Calculated_Work_Area_sqm": work_area,
            "Item Code": ITEM_CODE,
            "Units": "sq.m",
        }
    )

scenarios = pd.DataFrame(scenario_rows)


# --------------------------------------------------
# 5. Generate ML predictions
# --------------------------------------------------

predictions = model.predict(scenarios)

scenarios["Predicted_Cost_LKR"] = predictions

scenarios["Displayed_Cost_LKR"] = np.maximum(
    predictions,
    0.0,
)

scenarios["Cost_Change_From_Previous_LKR"] = (
    scenarios["Displayed_Cost_LKR"].diff()
)

scenarios["Prediction_Changed"] = (
    scenarios["Displayed_Cost_LKR"]
    .diff()
    .abs()
    .gt(0.01)
)

scenarios.loc[
    scenarios.index[0],
    "Prediction_Changed",
] = False


# --------------------------------------------------
# 6. Summarize sensitivity
# --------------------------------------------------

total_scenarios = len(scenarios)

unique_prediction_count = (
    scenarios["Displayed_Cost_LKR"]
    .round(2)
    .nunique()
)

change_count = int(
    scenarios["Prediction_Changed"].sum()
)

minimum_prediction = float(
    scenarios["Displayed_Cost_LKR"].min()
)

maximum_prediction = float(
    scenarios["Displayed_Cost_LKR"].max()
)

print("=" * 68)
print("STEP 28 - ML MODEL SENSITIVITY ANALYSIS")
print("=" * 68)

print("\nAlgorithm: Gradient Boosting Regressor")
print("Selected model: Model A - All Three Features")
print("Repair Item Code: 51")
print("Units: sq.m")

print(f"\nHistorical records for Item 51: {len(item_records)}")

print(
    f"Historical work-area range: "
    f"{minimum_area:,.2f} to "
    f"{maximum_area:,.2f} sqm"
)

print(f"\nTotal test scenarios: {total_scenarios}")

print(
    f"Unique predicted costs: "
    f"{unique_prediction_count}"
)

print(
    f"Number of prediction changes: "
    f"{change_count}"
)

print(
    f"\nMinimum predicted cost: "
    f"Rs. {minimum_prediction:,.2f}"
)

print(
    f"Maximum predicted cost: "
    f"Rs. {maximum_prediction:,.2f}"
)


# --------------------------------------------------
# 7. Display selected work-area examples
# --------------------------------------------------

print("\n" + "=" * 68)
print("SELECTED WORK-AREA PREDICTIONS")
print("=" * 68)

selected_areas = [
    22.5,
    30.0,
    45.0,
    60.0,
    75.0,
    90.0,
    105.0,
    112.5,
]

selected_rows = []

for target_area in selected_areas:

    nearest_index = (
        scenarios["Calculated_Work_Area_sqm"]
        .sub(target_area)
        .abs()
        .idxmin()
    )

    row = scenarios.loc[nearest_index]

    selected_rows.append(
        {
            "Work_Area_sqm": row[
                "Calculated_Work_Area_sqm"
            ],
            "Predicted_Cost_LKR": row[
                "Displayed_Cost_LKR"
            ],
        }
    )

selected_df = pd.DataFrame(selected_rows)

print(
    selected_df.to_string(
        index=False,
        float_format=lambda value: f"{value:,.2f}",
    )
)


# --------------------------------------------------
# 8. Display prediction change points
# --------------------------------------------------

print("\n" + "=" * 68)
print("PREDICTION CHANGE POINTS")
print("=" * 68)

change_points = scenarios[
    scenarios["Prediction_Changed"]
][
    [
        "Calculated_Work_Area_sqm",
        "Displayed_Cost_LKR",
        "Cost_Change_From_Previous_LKR",
    ]
]

if change_points.empty:

    print(
        "\nNo prediction changes detected "
        "within the tested area range."
    )

else:

    print(
        change_points.to_string(
            index=False,
            float_format=lambda value: f"{value:,.2f}",
        )
    )


# --------------------------------------------------
# 9. Save CSV reports
# --------------------------------------------------

scenarios_file = (
    OUTPUT_DIR
    / "model_sensitivity_predictions.csv"
)

changes_file = (
    OUTPUT_DIR
    / "model_sensitivity_change_points.csv"
)

scenarios.to_csv(
    scenarios_file,
    index=False,
)

change_points.to_csv(
    changes_file,
    index=False,
)


# --------------------------------------------------
# 10. Create sensitivity graph
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.plot(
    scenarios["Calculated_Work_Area_sqm"],
    scenarios["Displayed_Cost_LKR"],
    linewidth=2,
    label="ML Predicted Repair Cost",
)

plt.xlabel("Calculated Work Area (sqm)")
plt.ylabel("Predicted Repair Cost (LKR)")

plt.title(
    "Item Code 51 - ML Model Sensitivity to Work Area"
)

plt.grid(
    True,
    alpha=0.3,
)

plt.legend()
plt.tight_layout()

graph_file = (
    OUTPUT_DIR
    / "model_sensitivity_graph.png"
)

plt.savefig(
    graph_file,
    dpi=150,
)

plt.close()


# --------------------------------------------------
# 11. Final report
# --------------------------------------------------

print("\n" + "=" * 68)
print("SAVED OUTPUT FILES")
print("=" * 68)

print(f"\nPredictions: {scenarios_file}")
print(f"Change points: {changes_file}")
print(f"Graph: {graph_file}")

print("\nMODEL SENSITIVITY ANALYSIS COMPLETED!")
