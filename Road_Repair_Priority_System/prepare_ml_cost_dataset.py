
import pandas as pd
from pathlib import Path

# Project paths
project = Path(__file__).parent

input_file = (
    project / "datasets" /
    "Forecasted routine maintenance budget 2026.xlsx"
)

output_file = project / "outputs" / "ml_cost_dataset.csv"

# Load historical RDA records
df = pd.read_excel(input_file, sheet_name="Budget")

# Features and target
columns = [
    "RoadID",
    "StartChainage(m)",
    "EndChainage(m)",
    "Item Code",
    "Units",
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Total Amount (Rs.)"
]

ml_data = df[columns].copy()

# Rename prediction target
ml_data = ml_data.rename(
    columns={
        "Total Amount (Rs.)": "Repair_Cost_LKR"
    }
)

# Save prepared dataset
output_file.parent.mkdir(parents=True, exist_ok=True)
ml_data.to_csv(output_file, index=False)

# Print validation report
print("ML COST DATASET PREPARATION")
print("===========================")

print("\nTotal records:", len(ml_data))
print("Total columns:", len(ml_data.columns))

print("\nColumns:")
print(ml_data.columns.tolist())

print("\nMissing values:")
print(ml_data.isnull().sum().to_string())

print("\nRepair cost statistics:")
print(ml_data["Repair_Cost_LKR"].describe().to_string())

print("\nSaved dataset:", output_file)
print("\nML DATASET PREPARATION COMPLETED!")
