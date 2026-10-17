
from pathlib import Path

import numpy as np
import pandas as pd


# Define project paths
project = Path(__file__).resolve().parent

data_file = project / "outputs" / "ml_cost_dataset.csv"

predictions_file = (
    project / "outputs"
    / "item_code_accuracy_predictions.csv"
)


# Check required files
for file_path in [data_file, predictions_file]:

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )


# Load historical data and validation predictions
data = pd.read_csv(data_file)
predictions = pd.read_csv(predictions_file)


# Normalize item codes and road IDs
for frame in [data, predictions]:

    frame["Item Code"] = (
        frame["Item Code"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    frame["RoadID"] = (
        frame["RoadID"]
        .astype(str)
        .str.strip()
    )


# Convert historical numeric columns
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
    "Repair_Cost_LKR",
]

for column in numeric_columns:

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce",
    )


# Calculate work area from length and width
data["Calculated_Work_Area_sqm"] = (
    data["Length (m)"] * data["Width (m)"]
)


# Select historical records for Item Code 69
item_69 = data[
    data["Item Code"] == "69"
].copy()


# Select validation predictions for Item Code 69
pred_69 = predictions[
    predictions["Item Code"] == "69"
].copy()


print("=" * 70)
print("ITEM CODE 69 - PREDICTION ERROR INVESTIGATION")
print("=" * 70)

print("\nFocus Road: B0214")
print("Validation: Leave-One-Road-Out")
print("Model: Gradient Boosting without Road ID")

print(f"\nItem Code 69 historical records: {len(item_69)}")


# Display historical measurement values
print("\n" + "=" * 70)
print("1. HISTORICAL MEASUREMENTS FOR ITEM CODE 69")
print("=" * 70)

display_columns = [
    "RoadID",
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
    "Repair_Cost_LKR",
]

print(
    item_69[display_columns].to_string(
        index=False,
        float_format=lambda x: f"{x:,.2f}",
    )
)


# Show B0214 record
print("\n" + "=" * 70)
print("2. B0214 HISTORICAL RECORD")
print("=" * 70)

target = item_69[
    item_69["RoadID"] == "B0214"
]

if target.empty:

    print("No Item Code 69 record found for B0214.")

else:

    print(
        target[display_columns].to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}",
        )
    )


# Compare B0214 measurements against other roads
print("\n" + "=" * 70)
print("3. B0214 VS OTHER ROADS - MEASUREMENT COMPARISON")
print("=" * 70)

comparison_features = [
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Calculated_Work_Area_sqm",
]

other_roads = item_69[
    item_69["RoadID"] != "B0214"
]

if target.empty or other_roads.empty:

    print("Insufficient records for comparison.")

else:

    target_record = target.iloc[0]

    comparison_rows = []

    for feature in comparison_features:

        comparison_rows.append(
            {
                "Feature": feature,
                "B0214 Value": target_record[feature],
                "Other Roads Min": other_roads[feature].min(),
                "Other Roads Median": other_roads[feature].median(),
                "Other Roads Max": other_roads[feature].max(),
            }
        )

    comparison = pd.DataFrame(comparison_rows)

    print(
        comparison.to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}",
        )
    )


# Display Leave-One-Road-Out prediction errors
print("\n" + "=" * 70)
print("4. VALIDATION PREDICTION ERRORS - ITEM CODE 69")
print("=" * 70)

prediction_columns = [
    "RoadID",
    "Calculated_Work_Area_sqm",
    "Repair_Cost_LKR",
    "ML_Predicted_Cost_LKR",
    "Absolute_Error_LKR",
]

print(
    pred_69[prediction_columns].to_string(
        index=False,
        float_format=lambda x: f"{x:,.2f}",
    )
)


# Identify similar training records by work area
print("\n" + "=" * 70)
print("5. NEAREST WORK-AREA RECORDS TO B0214")
print("=" * 70)

if not target.empty and not other_roads.empty:

    target_area = float(
        target.iloc[0]["Calculated_Work_Area_sqm"]
    )

    similar = other_roads.copy()

    similar["Area_Difference_sqm"] = (
        similar["Calculated_Work_Area_sqm"]
        - target_area
    ).abs()

    similar = similar.sort_values(
        by="Area_Difference_sqm"
    )

    nearest_columns = [
        "RoadID",
        "Length (m)",
        "Width (m)",
        "Calculated_Work_Area_sqm",
        "Area_Difference_sqm",
        "Repair_Cost_LKR",
    ]

    print(
        similar[nearest_columns].to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}",
        )
    )


# Compare cost per calculated work area for diagnostics
print("\n" + "=" * 70)
print("6. HISTORICAL COST PER WORK AREA - DIAGNOSTIC ONLY")
print("=" * 70)

item_69["Cost_Per_Work_Area"] = np.where(
    item_69["Calculated_Work_Area_sqm"] > 0,
    item_69["Repair_Cost_LKR"]
    / item_69["Calculated_Work_Area_sqm"],
    np.nan,
)

print(
    item_69[
        [
            "RoadID",
            "Calculated_Work_Area_sqm",
            "Repair_Cost_LKR",
            "Cost_Per_Work_Area",
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:,.2f}",
    )
)

print(
    "\nNote: Cost per area is used only for "
    "historical data investigation."
)

print(
    "The ML cost prediction model is not "
    "being replaced by a rate formula."
)


print("\n" + "=" * 70)
print("INVESTIGATION COMPLETED!")
print("=" * 70)
