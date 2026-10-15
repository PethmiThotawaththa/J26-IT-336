
import pandas as pd
from pathlib import Path

# Project folders
project_folder = Path(__file__).parent
survey_folder = project_folder / "datasets" / "road_surveys"
output_folder = project_folder / "outputs"

output_folder.mkdir(exist_ok=True)

all_data = []

# Read all road survey CSV files
csv_files = sorted(survey_folder.glob("*.csv"))

for file in csv_files:

    print("Reading:", file.name)

    # Read CSV
    df = pd.read_csv(file, low_memory=False)

    # Get Road ID from filename
    road_id = file.stem.split("_")[0]

    # Get Road Side from filename
    if "_Left" in file.stem:
        road_side = "Left"
    elif "_Right" in file.stem:
        road_side = "Right"
    else:
        road_side = "Unspecified"

    # Add new columns
    df["Road_ID"] = road_id
    df["Road_Side"] = road_side

    # Remove empty Events column
    df = df.drop(columns=["Events"], errors="ignore")

    # Add to list
    all_data.append(df)

# Combine all files
combined_df = pd.concat(all_data, ignore_index=True)

# Save combined dataset
output_file = output_folder / "combined_road_surveys.csv"
combined_df.to_csv(output_file, index=False)

print("\nDATA COMBINATION COMPLETED!")
print("Total Rows:", len(combined_df))
print("Total Columns:", len(combined_df.columns))
print("Roads:", combined_df["Road_ID"].unique())
print("Sides:", combined_df["Road_Side"].unique())
print("Saved to:", output_file)
