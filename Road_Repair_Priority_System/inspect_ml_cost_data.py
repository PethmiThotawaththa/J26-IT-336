
import pandas as pd
from pathlib import Path

# Project paths
project = Path(__file__).parent

excel_file = (
    project
    / "datasets"
    / "Forecasted routine maintenance budget 2026.xlsx"
)

# Load RDA repair cost records
df = pd.read_excel(excel_file, sheet_name="Budget")

print("ML REPAIR COST DATA ANALYSIS")
print("============================")

print("\n1. DATASET SIZE")
print("Total Records:", len(df))
print("Total Columns:", len(df.columns))

# Important ML columns
columns = [
    "RoadID",
    "StartChainage(m)",
    "EndChainage(m)",
    "Inspection date",
    "Item Code",
    "Rate (Rs.)",
    "Quantity",
    "Total Amount (Rs.)"
]

print("\n2. MISSING VALUES")
print(df[columns].isna().sum())

print("\n3. REPAIR ACTIVITY DISTRIBUTION")
print(
    df["Item Code"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\n4. COST STATISTICS")
print(
    df["Total Amount (Rs.)"]
    .describe()
    .to_string()
)

print("\n5. QUANTITY STATISTICS")
print(
    df["Quantity"]
    .describe()
    .to_string()
)

print("\n6. ROAD DISTRIBUTION")
print(
    df["RoadID"]
    .value_counts()
    .to_string()
)

print("\n7. DATE RANGE")
dates = pd.to_datetime(
    df["Inspection date"],
    errors="coerce"
)

print("Earliest Date:", dates.min())
print("Latest Date:", dates.max())
print("Invalid Dates:", dates.isna().sum())

print("\n8. COST BY REPAIR ITEM")
item_summary = df.groupby("Item Code").agg(
    Records=("Item Code", "size"),
    Min_Cost=("Total Amount (Rs.)", "min"),
    Median_Cost=("Total Amount (Rs.)", "median"),
    Max_Cost=("Total Amount (Rs.)", "max")
)

print(item_summary.to_string())

print("\n9. POSSIBLE DATA LEAKAGE CHECK")

calculated_cost = (
    df["Rate (Rs.)"] * df["Quantity"]
)

difference = (
    df["Total Amount (Rs.)"] - calculated_cost
).abs()

print(
    "Records matching Rate x Quantity:",
    (difference <= 1).sum()
)

print(
    "Records not matching:",
    (difference > 1).sum()
)

print("\nML COST DATA INSPECTION COMPLETED!")
