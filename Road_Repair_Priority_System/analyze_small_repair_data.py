
from pathlib import Path

import numpy as np
import pandas as pd


# Define project paths
project = Path(__file__).resolve().parent

data_file = project / "outputs" / "ml_cost_dataset.csv"
output_file = (
    project / "outputs" / "small_repair_data_analysis.csv"
)


# Check the dataset
if not data_file.exists():
    raise FileNotFoundError(
        "Dataset not found: outputs/ml_cost_dataset.csv"
    )


# Load historical repair records
data = pd.read_csv(data_file)

required_columns = [
    "RoadID",
    "Item Code",
    "Units",
    "Length (m)",
    "Width (m)",
    "Area (sqm)",
    "Repair_Cost_LKR",
]

missing_columns = [
    col for col in required_columns
    if col not in data.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# Normalize item codes and units
data["Item Code"] = (
    data["Item Code"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

data["Units"] = (
    data["Units"].astype(str).str.strip()
)


# Convert measurements to numeric values
for column in [
    "Length (m)",
    "Width (m)",
    "Area (sqm)",
    "Repair_Cost_LKR",
]:
    data[column] = pd.to_numeric(
        data[column],
        errors="coerce",
    )


# Calculate work area from length and width
data["Calculated_Work_Area_sqm"] = (
    data["Length (m)"] * data["Width (m)"]
)


# Define work-area categories
def classify_work_area(area):

    if pd.isna(area) or not np.isfinite(area):
        return "Invalid measurement"

    if area < 0:
        return "Invalid measurement"

    if area == 0:
        return "Zero work area"

    if area <= 10:
        return "0-10 sqm"

    if area <= 50:
        return "10-50 sqm"

    if area <= 200:
        return "50-200 sqm"

    if area <= 750:
        return "200-750 sqm"

    return "Above 750 sqm"


data["Work_Area_Category"] = (
    data["Calculated_Work_Area_sqm"]
    .apply(classify_work_area)
)


# Set a consistent category order
category_order = [
    "Zero work area",
    "0-10 sqm",
    "10-50 sqm",
    "50-200 sqm",
    "200-750 sqm",
    "Above 750 sqm",
    "Invalid measurement",
]


# Print dataset overview
print("=" * 65)
print("SMALL REPAIR DATA AVAILABILITY ANALYSIS")
print("=" * 65)

print(f"\nTotal historical records: {len(data)}")
print(f"Total roads: {data['RoadID'].nunique()}")
print(f"Total Item Codes: {data['Item Code'].nunique()}")


# Show overall work-area distribution
print("\n" + "=" * 65)
print("1. OVERALL WORK AREA DISTRIBUTION")
print("=" * 65)

overall_counts = (
    data["Work_Area_Category"]
    .value_counts()
    .reindex(category_order, fill_value=0)
)

for category, count in overall_counts.items():

    percentage = (
        count / len(data) * 100
        if len(data) > 0 else 0
    )

    print(
        f"{category:<25} "
        f"{count:>4} records "
        f"({percentage:>5.1f}%)"
    )


# Analyze records by repair item
print("\n" + "=" * 65)
print("2. WORK AREA DISTRIBUTION BY ITEM CODE")
print("=" * 65)

item_summary = pd.crosstab(
    data["Item Code"],
    data["Work_Area_Category"],
)

item_summary = item_summary.reindex(
    columns=category_order,
    fill_value=0,
)

item_summary["Total Records"] = (
    item_summary.sum(axis=1)
)

item_summary["Positive Area Records"] = (
    item_summary[
        [
            "0-10 sqm",
            "10-50 sqm",
            "50-200 sqm",
            "200-750 sqm",
            "Above 750 sqm",
        ]
    ].sum(axis=1)
)

item_summary["Small Area Records (0-200 sqm)"] = (
    item_summary[
        [
            "0-10 sqm",
            "10-50 sqm",
            "50-200 sqm",
        ]
    ].sum(axis=1)
)

item_summary = item_summary.sort_values(
    by="Total Records",
    ascending=False,
)

print(item_summary.to_string())


# Focus on Item Code 69
print("\n" + "=" * 65)
print("3. ITEM CODE 69 - DETAILED ANALYSIS")
print("=" * 65)

item_69 = data[
    data["Item Code"] == "69"
].copy()

if item_69.empty:

    print("No historical records for Item Code 69.")

else:

    print(f"\nTotal records: {len(item_69)}")

    print("\nWork area categories:")

    counts_69 = (
        item_69["Work_Area_Category"]
        .value_counts()
        .reindex(category_order, fill_value=0)
    )

    for category, count in counts_69.items():
        print(f"{category:<25} {count:>4} records")

    positive_69 = item_69[
        item_69["Calculated_Work_Area_sqm"] > 0
    ]

    if not positive_69.empty:

        print("\nPositive work-area range:")

        minimum = (
            positive_69["Calculated_Work_Area_sqm"].min()
        )

        maximum = (
            positive_69["Calculated_Work_Area_sqm"].max()
        )

        print(f"Minimum: {minimum:,.2f} sqm")
        print(f"Maximum: {maximum:,.2f} sqm")

    print("\nHistorical Item Code 69 records:")

    display_columns = [
        "RoadID",
        "Item Code",
        "Units",
        "Length (m)",
        "Width (m)",
        "Calculated_Work_Area_sqm",
        "Repair_Cost_LKR",
    ]

    print(
        item_69[display_columns]
        .to_string(index=False)
    )


# Identify item codes with small repair examples
print("\n" + "=" * 65)
print("4. ITEM CODES WITH SMALL WORK AREAS")
print("=" * 65)

small_records = data[
    (data["Calculated_Work_Area_sqm"] > 0)
    & (data["Calculated_Work_Area_sqm"] <= 200)
].copy()

print(
    "\nHistorical records with positive "
    "work area up to 200 sqm:"
)

print(f"Total small-area records: {len(small_records)}")

if small_records.empty:

    print("No positive small-area records found.")

else:

    small_item_counts = (
        small_records["Item Code"]
        .value_counts()
        .sort_index()
    )

    print("\nSmall-area records by Item Code:")

    print(small_item_counts.to_string())


# Save analysis to CSV
item_summary.to_csv(
    output_file,
    index_label="Item Code",
)

print("\n" + "=" * 65)
print("5. SAVED ANALYSIS")
print("=" * 65)

print(f"\nSaved CSV: {output_file}")

print("\nANALYSIS COMPLETED!")
