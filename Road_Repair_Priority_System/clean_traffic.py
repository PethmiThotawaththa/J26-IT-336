
import pandas as pd
from pathlib import Path

project = Path(__file__).parent
data_folder = project / "datasets"
output_folder = project / "outputs"

output_folder.mkdir(exist_ok=True)

# Find Traffic Excel file
traffic_files = [
    f for f in data_folder.glob("*.xlsx")
    if "traffic" in f.name.lower()
]

if not traffic_files:
    raise FileNotFoundError("Traffic Excel file not found!")

traffic_file = traffic_files[0]

# Read Excel
df = pd.read_excel(
    traffic_file,
    sheet_name="Traffic Counts"
)

print("ORIGINAL TRAFFIC DATA")
print("=====================")
print("Rows:", len(df))

# Remove completely empty rows
df = df.dropna(how="all").copy()

print("After removing empty rows:", len(df))

# Standardize Road IDs
df["ROUTE NO"] = (
    df["ROUTE NO"]
    .astype("string")
    .str.strip()
    .str.upper()
)

# Convert important numeric columns
numeric_columns = [
    "Chainage (KM)",
    "TOTAL NO.OF VEH.",
    "HRS OF COUNT"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Convert count dates
df["DATE OF COUNT"] = pd.to_datetime(
    df["DATE OF COUNT"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# Calculate vehicles per hour
df["Vehicles_Per_Hour"] = (
    df["TOTAL NO.OF VEH."] /
    df["HRS OF COUNT"].replace(0, float("nan"))
)

# Check missing important values
print("\nMISSING IMPORTANT VALUES")
print(
    df[
        [
            "ROUTE NO",
            "Chainage (KM)",
            "DATE OF COUNT",
            "Vehicles_Per_Hour"
        ]
    ].isna().sum()
)

# Show road counts
print("\nRECORDS BY ROAD")
print(df["ROUTE NO"].value_counts(dropna=False))

# Save cleaned data
output_file = output_folder / "cleaned_traffic.csv"
df.to_csv(output_file, index=False)

print("\nCLEANING COMPLETED!")
print("Saved to:", output_file)
