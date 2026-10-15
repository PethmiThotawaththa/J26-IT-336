
import pandas as pd
from pathlib import Path

project = Path(__file__).parent
input_file = project / "outputs" / "cleaned_traffic.csv"
output_file = project / "outputs" / "final_traffic.csv"

# කලින් clean කරපු traffic data එක read කිරීම
df = pd.read_csv(input_file)

print("FINAL TRAFFIC DATA PREPARATION")
print("==============================")

print("Before filtering:", len(df))

# Keep actual traffic observations only
df = df.dropna(
    subset=[
        "ROUTE NO",
        "Chainage (KM)",
        "DATE OF COUNT",
        "Vehicles_Per_Hour"
    ]
).copy()

# Remove invalid traffic values
df = df[
    (df["Vehicles_Per_Hour"] >= 0)
    & (df["Chainage (KM)"] >= 0)
].copy()

# Rename columns
df = df.rename(columns={
    "ROUTE NO": "Road_ID",
    "Chainage (KM)": "Traffic_Chainage_km",
    "DATE OF COUNT": "Traffic_Date",
    "TOTAL NO.OF VEH.": "Total_Vehicles",
    "HRS OF COUNT": "Count_Hours"
})

# Save final dataset
df.to_csv(output_file, index=False)

print("After filtering:", len(df))

print("\nRecords by Road:")
print(df["Road_ID"].value_counts())

print("\nMissing Values:")
print(
    df[
        [
            "Road_ID",
            "Traffic_Chainage_km",
            "Traffic_Date",
            "Vehicles_Per_Hour"
        ]
    ].isna().sum()
)

print("\nFINAL TRAFFIC DATASET CREATED!")
print("Saved to:", output_file)
