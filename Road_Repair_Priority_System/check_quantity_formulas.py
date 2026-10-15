
import pandas as pd
from pathlib import Path

project = Path(__file__).parent

file_path = (
    project
    / "datasets"
    / "Forecasted routine maintenance budget 2026.xlsx"
)

df = pd.read_excel(file_path, sheet_name="Budget")

print("QUANTITY FORMULA CHECK")
print("======================")

# Select relevant item codes
selected_codes = [40, 51, 53, 59, 69, 70, 75]

columns = [
    "Item Code",
    "Units",
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Quantity"
]

for code in selected_codes:
    group = df[df["Item Code"] == code]

    print(f"\nITEM CODE: {code}")
    print("-" * 40)

    print(group[columns].to_string(index=False))

print("\nQUANTITY FORMULA CHECK COMPLETED!")
