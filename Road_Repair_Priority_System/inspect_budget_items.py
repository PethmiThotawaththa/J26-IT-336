
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
    raise FileNotFoundError("Budget Excel file not found!")

df = pd.read_excel(
    budget_files[0],
    sheet_name="Budget"
)

print("BUDGET ITEM CODE ANALYSIS")
print("=========================")

print("\nUnique Item Codes:")
print(df["Item Code"].nunique())

print("\nItem Code, Unit and Rate:")
items = (
    df.groupby(
        ["Item Code", "Units", "Rate (Rs.)"],
        dropna=False
    )
    .size()
    .reset_index(name="Record_Count")
    .sort_values("Item Code")
)

print(items.to_string(index=False))

print("\nTotal Amount by Item Code:")
amounts = (
    df.groupby("Item Code")["Total Amount (Rs.)"]
    .sum()
    .sort_values(ascending=False)
)

print(amounts.to_string())

print("\nITEM CODE ANALYSIS COMPLETED!")
