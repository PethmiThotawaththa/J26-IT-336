
import pandas as pd
from pathlib import Path

project = Path(__file__).parent
data_folder = project / "datasets"

# Find the budget Excel file
budget_files = [
    f for f in data_folder.glob("*.xlsx")
    if "forecast" in f.name.lower()
    or "budget" in f.name.lower()
]

if not budget_files:
    raise FileNotFoundError(
        "Budget Excel file not found!"
    )

budget_file = budget_files[0]

# Read Budget sheet
df = pd.read_excel(
    budget_file,
    sheet_name="Budget"
)

print("BUDGET DATA ANALYSIS")
print("====================")

print("Total Rows:", len(df))
print("File:", budget_file.name)

print("\nOriginal Road IDs:")
print(df["RoadID"].value_counts(dropna=False))


# Standardize road IDs
# Example: B0047 -> B047
def standardize_road_id(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    if value.startswith("B") and value[1:].isdigit():
        return "B" + str(int(value[1:])).zfill(3)

    return value


df["Road_ID"] = df["RoadID"].apply(
    standardize_road_id
)

# Convert numeric columns
numeric_columns = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Rate (Rs.)",
    "Quantity",
    "Total Amount (Rs.)"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Convert meters to kilometers
df["Start_Chainage_km"] = (
    df["StartChainage(m)"] / 1000
)

df["End_Chainage_km"] = (
    df["EndChainage(m)"] / 1000
)

print("\nStandardized Road IDs:")
print(df["Road_ID"].value_counts(dropna=False))

print("\nAllocated Budget by Road (Rs.):")
print(
    df.groupby("Road_ID")["Total Amount (Rs.)"]
    .sum(min_count=1)
    .to_string()
)

print("\nMissing Important Values:")
print(
    df[
        [
            "Road_ID",
            "Item Code",
            "Total Amount (Rs.)",
            "Start_Chainage_km",
            "End_Chainage_km"
        ]
    ].isna().sum()
)

print("\nChainage Range by Road:")
print(
    df.groupby("Road_ID").agg(
        Start_km=("Start_Chainage_km", "min"),
        End_km=("End_Chainage_km", "max")
    ).to_string()
)

print("\nBUDGET ANALYSIS COMPLETED!")
