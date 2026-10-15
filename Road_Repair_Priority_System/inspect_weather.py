
import pandas as pd
from pathlib import Path

project = Path(__file__).parent
data_folder = project / "datasets"

# Weather CSV file එක හොයනවා
weather_files = [
    f for f in data_folder.glob("*.csv")
    if "weather" in f.name.lower()
    or "whether" in f.name.lower()
]

if not weather_files:
    print("ERROR: Weather CSV file not found!")

else:
    weather_file = weather_files[0]

    print("WEATHER DATASET ANALYSIS")
    print("========================")
    print("File:", weather_file.name)

    # CSV read කිරීම
    df = pd.read_csv(weather_file, low_memory=False)

    print("\nTotal Rows:", len(df))
    print("Total Columns:", len(df.columns))

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nFirst 5 Rows:")
    print(df.head(5).to_string(index=False))

    print("\nMissing Values:")
    print(df.isna().sum().to_string())

    print("\nWEATHER ANALYSIS COMPLETED!")
