
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# Define project paths
project = Path(__file__).resolve().parent

model_file = (
    project / "models"
    / "repair_cost_model_without_road_id.joblib"
)

data_file = project / "outputs" / "ml_cost_dataset.csv"


# Check required files
if not model_file.exists():
    raise FileNotFoundError(
        "Model not found. Run "
        "train_cost_model_without_road_id.py first."
    )

if not data_file.exists():
    raise FileNotFoundError(
        "Historical ML dataset not found."
    )


# Load the trained ML model and historical data
model = joblib.load(model_file)
data = pd.read_csv(data_file)


# Normalize historical item codes
data["Item Code"] = (
    data["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

data["Units"] = data["Units"].astype(str).str.strip()
data["RoadID"] = data["RoadID"].astype(str).str.strip()


# Define the exact features used during training
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


# Read a non-negative numeric input
def ask_number(label, default):

    while True:
        value = input(f"{label} [{default:g}]: ").strip()

        if value == "":
            return float(default)

        try:
            number = float(value)

            if not np.isfinite(number) or number < 0:
                print("Enter a finite, non-negative number.")
                continue

            return number

        except ValueError:
            print("Invalid number. Try again.")


# Read a text input
def ask_text(label, default):

    value = input(f"{label} [{default}]: ").strip()

    return value if value else str(default)


print("=" * 60)
print("ML REPAIR COST - MEASUREMENT COMPARISON")
print("=" * 60)

print("\nModel: Gradient Boosting without Road ID")
print("Prediction method: Machine Learning")

print("\nThis demo compares two measurement scenarios.")


# Select a known repair item
known_codes = sorted(
    data["Item Code"].unique(),
    key=lambda code: (
        0,
        int(code)
    ) if code.isdigit() else (1, code),
)

default_code = (
    "69" if "69" in known_codes else known_codes[0]
)

print("\nAvailable historical Item Codes:")
print(", ".join(known_codes))

while True:

    item_code = ask_text(
        "Repair Item Code",
        default_code,
    )

    if item_code in known_codes:
        break

    print(
        "This Item Code has no training examples. "
        "Please select a listed code."
    )


# Select an example record for the chosen item
item_records = data[
    data["Item Code"] == item_code
].copy()

item_records["Length (m)"] = pd.to_numeric(
    item_records["Length (m)"],
    errors="coerce",
)

item_records["Width (m)"] = pd.to_numeric(
    item_records["Width (m)"],
    errors="coerce",
)

item_records["WorkArea"] = (
    item_records["Length (m)"]
    * item_records["Width (m)"]
)


# Prefer an example with a positive work area
positive_records = item_records[
    item_records["WorkArea"] > 0
]

if not positive_records.empty:
    example = positive_records.iloc[
        len(positive_records) // 2
    ]
else:
    example = item_records.iloc[0]


# Road ID is collected only for display
road_id = ask_text(
    "Road ID (for display only)",
    example["RoadID"],
)

units = str(example["Units"])

print(f"\nSelected Item Code: {item_code}")
print(f"Historical Units: {units}")

print(
    "\nOther numeric inputs will use values "
    "from the selected historical record."
)


# Prepare unchanged measurements
fixed_features = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
]

fixed_values = {}

for feature in fixed_features:

    value = pd.to_numeric(
        pd.Series([example[feature]]),
        errors="coerce",
    ).iloc[0]

    if not np.isfinite(value):
        raise ValueError(
            f"Invalid historical value for {feature}"
        )

    fixed_values[feature] = float(value)


# Collect measurements for Scenario A
print("\n" + "-" * 60)
print("SCENARIO A")
print("-" * 60)

length_a = ask_number(
    "Length (m)",
    float(example["Length (m)"]),
)

width_a = ask_number(
    "Width (m)",
    float(example["Width (m)"]),
)


# Collect measurements for Scenario B
print("\n" + "-" * 60)
print("SCENARIO B")
print("-" * 60)

length_b = ask_number(
    "Length (m)",
    length_a * 1.5 if length_a > 0 else 1.0,
)

width_b = ask_number(
    "Width (m)",
    width_a,
)


# Build an ML input record
def build_input(length, width):

    return {
        **fixed_values,
        "Length (m)": length,
        "Width (m)": width,
        "Calculated_Work_Area_sqm": length * width,
        "Item Code": item_code,
        "Units": units,
    }


scenario_a = build_input(length_a, width_a)
scenario_b = build_input(length_b, width_b)

X_new = pd.DataFrame([
    scenario_a,
    scenario_b,
])

X_new = X_new[
    numeric_features + categorical_features
]


# Generate both predictions using the trained ML model
predictions = model.predict(X_new)

cost_a = float(predictions[0])
cost_b = float(predictions[1])

area_a = length_a * width_a
area_b = length_b * width_b


# Check historical work-area range for this item
historical_areas = positive_records["WorkArea"]

if not historical_areas.empty:

    minimum_area = historical_areas.min()
    maximum_area = historical_areas.max()

    print("\nHistorical positive work-area range:")
    print(
        f"{minimum_area:,.2f} to "
        f"{maximum_area:,.2f} sqm"
    )

    for label, area in [
        ("A", area_a),
        ("B", area_b),
    ]:
        if area < minimum_area or area > maximum_area:
            print(
                f"WARNING: Scenario {label} work area "
                "is outside the historical range "
                "for this Item Code."
            )


# Display comparison results
print("\n" + "=" * 60)
print("ML COST PREDICTION COMPARISON")
print("=" * 60)

print(f"\nRoad ID (display only): {road_id}")
print(f"Item Code: {item_code}")
print(f"Units: {units}")

print("\nSCENARIO A")
print(f"Length: {length_a:,.2f} m")
print(f"Width: {width_a:,.2f} m")
print(f"Calculated Work Area: {area_a:,.2f} sqm")
print(f"ML Predicted Cost: Rs. {cost_a:,.2f}")

print("\nSCENARIO B")
print(f"Length: {length_b:,.2f} m")
print(f"Width: {width_b:,.2f} m")
print(f"Calculated Work Area: {area_b:,.2f} sqm")
print(f"ML Predicted Cost: Rs. {cost_b:,.2f}")

difference = cost_b - cost_a

print("\nCOST COMPARISON")
print(f"Predicted Cost Difference: Rs. {difference:,.2f}")

if difference > 0:
    print("Scenario B has a higher predicted cost.")
elif difference < 0:
    print("Scenario B has a lower predicted cost.")
else:
    print("Both scenarios have the same predicted cost.")

print("\nCOMPARISON COMPLETED!")
