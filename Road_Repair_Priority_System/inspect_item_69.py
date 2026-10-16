
from pathlib import Path

import pandas as pd


# Define project paths
project = Path(__file__).parent

input_file = (
    project / "outputs" / "road_validation_predictions.csv"
)

output_file = (
    project / "outputs" / "item_69_analysis.csv"
)


# Load detailed road validation predictions
df = pd.read_csv(input_file)

# Standardize item codes
df["Item Code"] = df["Item Code"].astype(str)


# Select Item Code 69 records
item_df = df[df["Item Code"] == "69"].copy()

if item_df.empty:
    raise ValueError("No records found for Item Code 69.")


# Calculate repair work area from recorded dimensions
item_df["Calculated_Area_sqm"] = (
    item_df["Length (m)"] * item_df["Width (m)"]
)


# Calculate prediction error
item_df["Signed_Error_LKR"] = (
    item_df["RF_Predicted_LKR"]
    - item_df["Actual_Cost_LKR"]
)

item_df["Absolute_Error_LKR"] = (
    item_df["Signed_Error_LKR"].abs()
)


# Compare each held-out record against other roads
outside_range = []
training_min_areas = []
training_max_areas = []

for _, row in item_df.iterrows():

    # Other roads form the training data for this test road
    training_rows = item_df[
        item_df["RoadID"] != row["RoadID"]
    ]

    min_area = training_rows["Calculated_Area_sqm"].min()
    max_area = training_rows["Calculated_Area_sqm"].max()

    test_area = row["Calculated_Area_sqm"]

    is_outside = (
        test_area < min_area or test_area > max_area
    )

    training_min_areas.append(min_area)
    training_max_areas.append(max_area)
    outside_range.append(is_outside)


# Add dimension range comparison results
item_df["Training_Min_Area_sqm"] = training_min_areas
item_df["Training_Max_Area_sqm"] = training_max_areas
item_df["Area_Outside_Training_Range"] = outside_range


# Select useful analysis columns
display_columns = [
    "RoadID",
    "Item Code",
    "Length (m)",
    "Width (m)",
    "Calculated_Area_sqm",
    "Actual_Cost_LKR",
    "RF_Predicted_LKR",
    "Absolute_Error_LKR",
    "Training_Min_Area_sqm",
    "Training_Max_Area_sqm",
    "Area_Outside_Training_Range"
]


# Display the analysis report
print("ITEM CODE 69 DETAILED ANALYSIS")
print("==============================")

print("Total records:", len(item_df))

print(
    "\nAverage Absolute Error (LKR):",
    round(item_df["Absolute_Error_LKR"].mean(), 2)
)

print(
    "Records outside training area range:",
    int(item_df["Area_Outside_Training_Range"].sum())
)


# Display all Item Code 69 records
print("\nALL ITEM CODE 69 RECORDS")
print("========================")

print(
    item_df[display_columns]
    .sort_values(
        "Absolute_Error_LKR",
        ascending=False
    )
    .to_string(index=False)
)


# Save the detailed analysis
item_df[display_columns].to_csv(
    output_file,
    index=False
)

print("\nSaved analysis:", output_file)
print("\nITEM CODE 69 ANALYSIS COMPLETED!")
