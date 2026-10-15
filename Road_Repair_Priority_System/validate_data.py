
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).parent

file_path = project_folder / "outputs" / "combined_road_surveys.csv"

df = pd.read_csv(file_path, low_memory=False)

print("COMBINED DATA VALIDATION")
print("========================")

# Check total rows and columns
print("Total Rows:", len(df))
print("Total Columns:", len(df.columns))

# Check roads and sides
print("\nRecords by Road and Side:")
print(df.groupby(["Road_ID", "Road_Side"]).size())

# Convert survey dates
df["Survey_Date"] = pd.to_datetime(
    df["Survey_Date"],
    format="mixed",
    errors="coerce"
)

print("\nInvalid Survey Dates:")
print(df["Survey_Date"].isna().sum())

# Check GPS coordinates
latitude = pd.to_numeric(
    df["Latitude__deg_"], errors="coerce"
)

longitude = pd.to_numeric(
    df["Longitude__deg_"], errors="coerce"
)

invalid_gps = (
    latitude.isna()
    | longitude.isna()
    | ~latitude.between(-90, 90)
    | ~longitude.between(-180, 180)
)

print("\nInvalid GPS Coordinates:")
print(invalid_gps.sum())

# Check chainage
chainage = pd.to_numeric(
    df["Chainage__km_"], errors="coerce"
)

invalid_chainage = chainage.isna() | (chainage < 0)

print("\nInvalid Chainage Values:")
print(invalid_chainage.sum())

# Check image filenames
print("\nMissing Image Filenames:")
print(df["Image_Filename"].isna().sum())

print("\nVALIDATION COMPLETED!")
