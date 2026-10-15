
import pandas as pd
from pathlib import Path

project = Path(__file__).parent

input_file = project / "datasets" / "Whether.csv"
output_file = project / "outputs" / "cleaned_weather.csv"

# Read original weather dataset
df = pd.read_csv(input_file)

print("WEATHER DATA CLEANING")
print("=====================")

print("Original Rows:", len(df))

# Create proper Date column
df["Date"] = pd.to_datetime(
    df[["year", "month", "day"]],
    errors="coerce"
)

# Convert weather measurements to numeric
weather_columns = [
    "temp", "tmin", "tmax",
    "rhum", "prcp", "wspd",
    "pres", "cldc"
]

for col in weather_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

print("\nInvalid Dates:")
print(df["Date"].isna().sum())

print("\nDuplicate Dates:")
print(df["Date"].duplicated().sum())

print("\nDate Range:")
print("Start:", df["Date"].min())
print("End:", df["Date"].max())

print("\nMissing Rainfall Records:")
print(
    df.loc[
        df["prcp"].isna(),
        ["Date", "prcp", "prcp_source"]
    ].to_string(index=False)
)

print("\nMissing Weather Measurements:")
print(df[weather_columns].isna().sum())

# Sort by date
df = df.sort_values("Date")

# Save without inventing rainfall values
df.to_csv(output_file, index=False)

print("\nCLEANING COMPLETED!")
print("Saved to:", output_file)
