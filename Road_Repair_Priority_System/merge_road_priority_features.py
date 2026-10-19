
from pathlib import Path
import pandas as pd

# Input files
BASE_FILE = Path("outputs/road_priority_inputs_unlabelled.csv")
LOCATION_FILE = Path("outputs/road_nearby_location_features.csv")

# New output file - original datasets stay unchanged
OUTPUT_FILE = Path("outputs/road_priority_features_combined_unlabelled.csv")

# Check files
for file in [BASE_FILE, LOCATION_FILE]:
    if not file.exists():
        raise FileNotFoundError(f"File not found: {file}")

# Load datasets
base = pd.read_csv(BASE_FILE)
locations = pd.read_csv(LOCATION_FILE)

# Validate road IDs
for name, df in [("Base", base), ("Locations", locations)]:
    if "road_id" not in df.columns:
        raise ValueError(f"{name} dataset has no road_id column")

    df["road_id"] = df["road_id"].astype(str).str.strip().str.upper()

    if df["road_id"].duplicated().any():
        raise ValueError(
            f"{name} dataset has duplicate road IDs: "
            f"{df.loc[df['road_id'].duplicated(), 'road_id'].tolist()}"
        )

# Confirm all base roads have location features
missing_roads = set(base["road_id"]) - set(locations["road_id"])

if missing_roads:
    raise ValueError(
        f"Location features missing for roads: {sorted(missing_roads)}"
    )

# Merge using road_id
combined = base.merge(
    locations,
    on="road_id",
    how="left",
    validate="one_to_one"
)

# Save new combined dataset
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
combined.to_csv(OUTPUT_FILE, index=False)

print("\n" + "=" * 60)
print("ROAD PRIORITY FEATURE MERGE COMPLETED")
print("=" * 60)

print("Output file:", OUTPUT_FILE)
print("Total roads:", len(combined))
print("Total columns:", len(combined.columns))

print("\nLOCATION FEATURES:")
columns = [
    "road_id",
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "nearby_fire_station_count_500m",
]

print(combined[columns].to_string(index=False))

print("\nPRIORITY LABEL STATUS:")
if "priority_label" in combined.columns:
    print(
        "Non-empty priority labels:",
        combined["priority_label"].notna().sum()
    )
else:
    print("Priority label column not found")

print("\nNOTE: This is a feature dataset, not a trained ML model.")
