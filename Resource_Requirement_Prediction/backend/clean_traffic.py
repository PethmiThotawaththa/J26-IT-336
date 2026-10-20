from pathlib import Path
import pandas as pd

project = Path.cwd()
source = Path(
    r"D:\Y4S1\RP\PP1\RESOURCES\RDA"
    r"\Traffic Data of Roads (B047, B174, B214, B240, B263 and B435).xlsx"
)
output = project / "data" / "processed" / "traffic_clean.csv"
output.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(source, sheet_name="Traffic Counts")
df["Source_Excel_Row"] = range(2, len(df) + 2)

# Standardize road IDs: B47 and B0047 become B047
def normalize_road_id(value):
    if pd.isna(value):
        return pd.NA
    value = str(value).strip().upper()
    if value.startswith("B") and value[1:].isdigit():
        return "B" + value[1:].lstrip("0").zfill(3)
    return pd.NA

df["RoadID"] = df["ROUTE NO"].apply(normalize_road_id)

# Parse mixed date formats, including 27/08/2024 and 05.09.2024
df["Traffic_Date"] = pd.to_datetime(
    df["DATE OF COUNT"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# Remove blank/explanatory rows, not genuine dated traffic observations
before = len(df)
df = df[
    df["RoadID"].notna()
    & df["Traffic_Date"].notna()
].copy()

# Standardize useful column names
df = df.rename(columns={
    "NAME OF ROAD": "Road_Name",
    "Chainage (KM)": "Chainage_KM",
    "STATION": "Station",
    "TOTAL NO.OF VEH.": "Total_Vehicles",
    "HRS OF COUNT": "Count_Hours"
})

df.to_csv(output, index=False, encoding="utf-8-sig")

print("Traffic cleaning completed")
print("Original worksheet rows:", before)
print("Kept dated traffic records:", len(df))
print("Removed blank/explanatory rows:", before - len(df))
print("Road IDs:", sorted(df["RoadID"].unique()))
print("Date range:", df["Traffic_Date"].min(), "to", df["Traffic_Date"].max())
print("Output:", output)
print("\nRecords by road:")
print(df["RoadID"].value_counts().sort_index().to_string())
