
import pandas as pd
from pathlib import Path

# Project folders
project = Path(__file__).parent
output_folder = project / "outputs"
output_folder.mkdir(exist_ok=True)

# Verified HSR 2025 Colombo repair rates
repair_rates = [
    {
        "HSR_Code": "MS1-002",
        "Repair_Activity": "Shallow pothole patching with hot bitumen (<20 mm)",
        "Unit": "sq.m",
        "Rate_LKR": 396.25,
        "Cost_Notes": "Excludes transport of aggregate and bitumen"
    },
    {
        "HSR_Code": "MS1-003",
        "Repair_Activity": "Shallow pothole patching with MC30 bitumen (<20 mm)",
        "Unit": "sq.m",
        "Rate_LKR": 420.50,
        "Cost_Notes": "Excludes transport of aggregate and bitumen"
    },
    {
        "HSR_Code": "MS1-004",
        "Repair_Activity": "Shallow pothole patching with CRS-1 emulsion (<20 mm)",
        "Unit": "sq.m",
        "Rate_LKR": 343.05,
        "Cost_Notes": "Excludes transport of aggregate"
    },
    {
        "HSR_Code": "MS1-005",
        "Repair_Activity": "Medium pothole patching with site-made premix (20-75 mm)",
        "Unit": "sq.m",
        "Rate_LKR": 2949.50,
        "Cost_Notes": "Excludes transport of aggregate"
    },
    {
        "HSR_Code": "MS1-006",
        "Repair_Activity": "Pothole patching with plant-made bitumen bound base",
        "Unit": "m.ton",
        "Rate_LKR": 20167.65,
        "Cost_Notes": "Premix included; transport paid separately"
    },
    {
        "HSR_Code": "MS1-007",
        "Repair_Activity": "Medium pothole patching with graded aggregate (20-75 mm)",
        "Unit": "sq.m",
        "Rate_LKR": 1708.85,
        "Cost_Notes": "Excludes transport of aggregate and bitumen"
    },
    {
        "HSR_Code": "MS1-008",
        "Repair_Activity": "Deep pothole premix surface layer (>75 mm)",
        "Unit": "sq.m",
        "Rate_LKR": 1666.20,
        "Cost_Notes": "Underlying aggregate/gravel paid separately; excludes transport"
    },
    {
        "HSR_Code": "MS1-009",
        "Repair_Activity": "Deep pothole water-bound gravel work (>75 mm)",
        "Unit": "sq.m",
        "Rate_LKR": 100.70,
        "Cost_Notes": "Aggregate and gravel paid separately"
    },
    {
        "HSR_Code": "S1-035",
        "Repair_Activity": "Manual sand sealing",
        "Unit": "sq.m",
        "Rate_LKR": 196.20,
        "Cost_Notes": "Pothole patching and external transport paid separately"
    },
    {
        "HSR_Code": "S1-035A",
        "Repair_Activity": "Minor pothole patching before sand sealing",
        "Unit": "sq.m",
        "Rate_LKR": 30.45,
        "Cost_Notes": "Use only with applicable sand-sealing work"
    },
    {
        "HSR_Code": "S1-036C",
        "Repair_Activity": "Crack sealing with CSS-1 emulsion using plant",
        "Unit": "sq.m",
        "Rate_LKR": 242.65,
        "Cost_Notes": "Plant/equipment conditions apply; other work paid separately"
    },
    {
        "HSR_Code": "MN1-001",
        "Repair_Activity": "Hot bitumen road-surface patching, 14 L per half-km",
        "Unit": "half-km",
        "Rate_LKR": 5208.65,
        "Cost_Notes": "Rate is per half-kilometre, not per sq.m"
    }
]

df = pd.DataFrame(repair_rates)

df["Source_Year"] = 2025
df["Source_District"] = "Colombo"
df["Source_Document"] = "HSR Summary 2025 Colombo"

# Save dataset
output_file = output_folder / "repair_rates.csv"
df.to_csv(output_file, index=False)

# Validation
print("HSR REPAIR RATES DATASET")
print("========================")
print("Total Repair Items:", len(df))
print("Missing Rates:", df["Rate_LKR"].isna().sum())
print("Duplicate HSR Codes:", df["HSR_Code"].duplicated().sum())

print("\nRepair Rates:")
print(
    df[
        ["HSR_Code", "Repair_Activity", "Unit", "Rate_LKR"]
    ].to_string(index=False)
)

print("\nSaved To:", output_file)
print("\nREPAIR RATES DATASET CREATED!")
