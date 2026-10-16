
from pathlib import Path

import pandas as pd


# Define project paths
project = Path(__file__).parent

input_file = (
    project / "outputs" / "ml_cost_dataset.csv"
)

output_file = (
    project / "outputs" / "item_69_unit_cost.csv"
)


# Load historical repair records
df = pd.read_csv(input_file)


# Select Item Code 69
df["Item Code"] = df["Item Code"].astype(str)

item_df = df[
    df["Item Code"] == "69"
].copy()


# Calculate recorded repair-work area
item_df["Calculated_Area_sqm"] = (
    item_df["Length (m)"]
    * item_df["Width (m)"]
)


# Avoid division by zero
item_df = item_df[
    item_df["Calculated_Area_sqm"] > 0
].copy()


# Calculate the observed cost per square meter
item_df["Cost_Per_sqm_LKR"] = (
    item_df["Repair_Cost_LKR"]
    / item_df["Calculated_Area_sqm"]
)


# Display summary statistics
print("ITEM CODE 69 UNIT COST ANALYSIS")
print("===============================")

print("Total records:", len(item_df))

print(
    "Minimum cost per sqm (LKR):",
    round(item_df["Cost_Per_sqm_LKR"].min(), 2)
)

print(
    "Maximum cost per sqm (LKR):",
    round(item_df["Cost_Per_sqm_LKR"].max(), 2)
)

print(
    "Average cost per sqm (LKR):",
    round(item_df["Cost_Per_sqm_LKR"].mean(), 2)
)


# Display all item records
print("\nITEM CODE 69 UNIT COST DETAILS")
print("=============================")

columns = [
    "RoadID",
    "Item Code",
    "Length (m)",
    "Width (m)",
    "Calculated_Area_sqm",
    "Repair_Cost_LKR",
    "Cost_Per_sqm_LKR"
]

print(
    item_df[columns].to_string(index=False)
)


# Save the analysis results
item_df[columns].to_csv(
    output_file,
    index=False
)

print("\nSaved analysis:", output_file)
print("\nUNIT COST ANALYSIS COMPLETED!")
