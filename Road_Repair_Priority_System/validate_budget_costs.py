
import pandas as pd
from pathlib import Path

project = Path(__file__).parent
data_folder = project / "datasets"

budget_files = [
    f for f in data_folder.glob("*.xlsx")
    if "forecast" in f.name.lower()
    or "budget" in f.name.lower()
]

if not budget_files:
    raise FileNotFoundError(
        "Budget Excel file not found!"
    )

df = pd.read_excel(
    budget_files[0],
    sheet_name="Budget"
)

print("BUDGET COST VALIDATION")
print("======================")

# Convert financial columns to numbers
columns = [
    "Rate (Rs.)",
    "Quantity",
    "Total Amount (Rs.)"
]

for col in columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Calculate expected cost
df["Calculated_Cost"] = (
    df["Rate (Rs.)"] * df["Quantity"]
)

# Compare with budget amount
df["Cost_Difference"] = (
    df["Total Amount (Rs.)"]
    - df["Calculated_Cost"]
).abs()

# Allow small rounding differences
tolerance = 1.00

mismatches = df[
    df["Cost_Difference"] > tolerance
]

print("\nTotal Records:", len(df))

print("\nMissing Financial Values:")
print(df[columns].isna().sum())

print("\nRecords with Cost Difference > Rs. 1:")
print(len(mismatches))

print("\nLargest Cost Difference:")
print(df["Cost_Difference"].max())

print("\nMismatch Details:")
print(
    mismatches[
        [
            "RoadID",
            "Item Code",
            "Rate (Rs.)",
            "Quantity",
            "Total Amount (Rs.)",
            "Calculated_Cost",
            "Cost_Difference"
        ]
    ].to_string(index=False)
)

print("\nBUDGET COST VALIDATION COMPLETED!")
