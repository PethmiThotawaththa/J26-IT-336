
from pathlib import Path

import joblib
import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

MODEL_FILE = Path(
    "models/final_extra_trees_cost_model.joblib"
)

DATA_FILE = Path(
    "outputs/ml_cost_dataset.csv"
)


# --------------------------------------------------
# Load trained ML model and historical data
# --------------------------------------------------

if not MODEL_FILE.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_FILE}"
    )

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )

model_package = joblib.load(MODEL_FILE)

model = model_package["model"]
input_features = model_package["input_features"]

historical_df = pd.read_csv(DATA_FILE)

historical_df["Item Code"] = (
    pd.to_numeric(
        historical_df["Item Code"],
        errors="coerce"
    )
    .astype("Int64")
    .astype(str)
)

historical_df["Units"] = (
    historical_df["Units"]
    .astype(str)
    .str.strip()
)

historical_df["Calculated_Work_Area_sqm"] = (
    historical_df["Length (m)"].fillna(0)
    * historical_df["Width (m)"].fillna(0)
)


# --------------------------------------------------
# Input helper functions
# --------------------------------------------------

def get_required_text(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field cannot be empty.")


def get_nonnegative_number(prompt):
    while True:
        value = input(prompt).strip()

        if value == "":
            return 0.0

        try:
            number = float(value)

            if not (
                number >= 0
                and number < float("inf")
            ):
                print(
                    "Please enter a finite "
                    "non-negative number."
                )
                continue

            return number

        except ValueError:
            print("Please enter a valid number.")


def normalize_item_code(value):
    try:
        number = float(value)

        if number.is_integer():
            return str(int(number))

    except ValueError:
        pass

    return value.strip()


# --------------------------------------------------
# Program heading
# --------------------------------------------------

print("\n" + "=" * 65)
print("AI-BASED ROAD REPAIR COST PREDICTION SYSTEM")
print("=" * 65)

print("\nML Algorithm: Extra Trees Regressor")
print("Prediction Type: Estimated Repair Cost (LKR)")
print("Road ID and Chainage are not ML input features.")


# --------------------------------------------------
# Repair item and road details
# --------------------------------------------------

print("\n" + "-" * 65)
print("REPAIR DETAILS")
print("-" * 65)

item_code = normalize_item_code(
    get_required_text("Repair Item Code : ")
)

road_id = get_required_text("Road ID : ")

matching_records = historical_df[
    historical_df["Item Code"] == item_code
].copy()

if matching_records.empty:
    print(
        "\nWARNING: This Item Code is not present "
        "in the historical training dataset."
    )
    print(
        "Prediction may be unreliable for "
        "an unseen repair activity."
    )

    units = get_required_text("Units : ")

else:
    available_units = sorted(
        matching_records["Units"]
        .dropna()
        .unique()
        .tolist()
    )

    if len(available_units) == 1:
        units = available_units[0]
        print(f"Units : {units} (automatically selected)")

    else:
        print(
            "\nHistorical units for this item:",
            ", ".join(available_units)
        )

        units = get_required_text("Units : ")

        if units not in available_units:
            print(
                "WARNING: The selected Units were "
                "not observed for this Item Code."
            )


# --------------------------------------------------
# Repair measurements
# --------------------------------------------------

print("\n" + "-" * 65)
print("REPAIR MEASUREMENTS")
print("-" * 65)

print(
    "Leave a numeric field blank to use 0."
)

length = get_nonnegative_number(
    "Length (m) : "
)

width = get_nonnegative_number(
    "Width (m) : "
)

depth = get_nonnegative_number(
    "Depth (m) : "
)

historical_area = get_nonnegative_number(
    "Historical Area Field (sqm) : "
)

count = get_nonnegative_number(
    "Count : "
)

frequency = get_nonnegative_number(
    "Times per Year (Frequency) : "
)

density = get_nonnegative_number(
    "Density (kg/m3) : "
)

calculated_work_area = length * width


# --------------------------------------------------
# Build model input
# --------------------------------------------------

input_data = {
    "Depth (m)": depth,
    "Area (sqm)": historical_area,
    "Count": count,
    "Times per year (Frequency)": frequency,
    "Density (kg/m3)": density,
    "Length (m)": length,
    "Width (m)": width,
    "Calculated_Work_Area_sqm": calculated_work_area,
    "Item Code": item_code,
    "Units": units,
}

input_df = pd.DataFrame([input_data])

input_df = input_df[input_features]


# --------------------------------------------------
# Predict repair cost using machine learning
# --------------------------------------------------

raw_prediction = float(
    model.predict(input_df)[0]
)

predicted_cost = max(0.0, raw_prediction)


# --------------------------------------------------
# Check historical work-area range
# --------------------------------------------------

prediction_status = "Limited historical support"
range_message = ""

if not matching_records.empty:

    same_unit_records = matching_records[
        matching_records["Units"] == units
    ]

    positive_areas = same_unit_records[
        same_unit_records[
            "Calculated_Work_Area_sqm"
        ] > 0
    ]["Calculated_Work_Area_sqm"]

    if not positive_areas.empty:

        min_area = float(positive_areas.min())
        max_area = float(positive_areas.max())

        range_message = (
            f"Historical Positive Work-Area Range: "
            f"{min_area:,.2f} - {max_area:,.2f} sqm"
        )

        if (
            calculated_work_area >= min_area
            and calculated_work_area <= max_area
        ):
            prediction_status = (
                "Within historical work-area range"
            )

        else:
            prediction_status = (
                "Outside historical work-area range"
            )

    else:
        prediction_status = (
            "No positive historical work-area "
            "examples for this Item Code and Units"
        )


# --------------------------------------------------
# Display prediction results
# --------------------------------------------------

print("\n" + "=" * 65)
print("ML REPAIR COST PREDICTION RESULT")
print("=" * 65)

print(f"\nRoad ID: {road_id}")
print(f"Repair Item Code: {item_code}")
print(f"Units: {units}")

print(f"\nLength: {length:,.2f} m")
print(f"Width: {width:,.3f} m")

print(
    f"Calculated Work Area: "
    f"{calculated_work_area:,.2f} sqm"
)

print("\n" + "-" * 65)

print(
    f"PREDICTED REPAIR COST: "
    f"Rs. {predicted_cost:,.2f}"
)

print("-" * 65)

print(f"\nPrediction Status: {prediction_status}")

if range_message:
    print(range_message)

if raw_prediction < 0:
    print(
        "Note: A negative raw prediction "
        "was displayed as zero."
    )

print(
    "\nThis is an ML-based estimate learned "
    "from historical RDA costing records."
)

print(
    "It is not a verified final contractor "
    "payment or quotation."
)

print(
    "Being within the historical area range "
    "does not guarantee accuracy."
)

print("\n" + "=" * 65)
