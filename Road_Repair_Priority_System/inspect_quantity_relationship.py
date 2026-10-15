
import pandas as pd
from pathlib import Path

project = Path(__file__).parent

file_path = (
    project
    / "datasets"
    / "Forecasted routine maintenance budget 2026.xlsx"
)

df = pd.read_excel(file_path, sheet_name="Budget")

print("QUANTITY RELATIONSHIP ANALYSIS")
print("==============================")

# Check whether quantities can be explained
# by available measurement fields.

measurements = [
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Weight (m.ton)"
]

print("\n1. MEASUREMENT USAGE BY ITEM CODE")

for code, group in df.groupby("Item Code"):
    print(f"\nItem Code: {code}")
    print("Records:", len(group))
    print("Unit:", group["Units"].iloc[0])

    for column in measurements:
        non_zero = (group[column] != 0).sum()
        print(f"  {column}: {non_zero} non-zero")

print("\n2. QUANTITY VS AREA")

area_records = df[df["Area (sqm)"] > 0]

print("Records with Area > 0:", len(area_records))

if not area_records.empty:
    print(
        area_records[
            ["Item Code", "Units",
             "Area (sqm)", "Quantity"]
        ].head(15).to_string(index=False)
    )

print("\n3. QUANTITY VS LENGTH AND WIDTH")

size_records = df[
    (df["Length (m)"] > 0)
    & (df["Width (m)"] > 0)
].copy()

print(
    "Records with Length and Width > 0:",
    len(size_records)
)

if not size_records.empty:
    size_records["Length_x_Width"] = (
        size_records["Length (m)"]
        * size_records["Width (m)"]
    )

    print(
        size_records[
            ["Item Code", "Units",
             "Length_x_Width", "Quantity"]
        ].head(15).to_string(index=False)
    )

print("\nQUANTITY RELATIONSHIP ANALYSIS COMPLETED!")
