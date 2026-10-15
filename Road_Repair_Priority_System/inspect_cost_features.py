
import pandas as pd
from pathlib import Path

project = Path(__file__).parent

file_path = (
    project
    / "datasets"
    / "Forecasted routine maintenance budget 2026.xlsx"
)

df = pd.read_excel(file_path, sheet_name="Budget")

print("ML COST FEATURE INSPECTION")
print("==========================")

print("\n1. ALL COLUMNS")
for column in df.columns:
    print(column)

print("\n2. COLUMN DATA TYPES")
print(df.dtypes.to_string())

print("\n3. NON-MISSING VALUES")
print(df.notna().sum().to_string())

print("\n4. MEASUREMENT COLUMN STATISTICS")

measurement_columns = [
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Quantity"
]

for column in measurement_columns:
    if column in df.columns:
        values = pd.to_numeric(
            df[column], errors="coerce"
        )

        print(f"\n{column}")
        print("Available:", values.notna().sum())
        print("Non-zero:", (values.fillna(0) != 0).sum())
        print("Minimum:", values.min())
        print("Maximum:", values.max())

print("\n5. ITEM CODE AND UNIT COMBINATIONS")
print(
    df.groupby(["Item Code", "Units"])
    .size()
    .to_string()
)

print("\nML COST FEATURE INSPECTION COMPLETED!")
