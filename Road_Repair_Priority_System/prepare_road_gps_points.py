
from pathlib import Path
import re

import pandas as pd

SURVEY_FOLDER = Path("datasets/road_surveys")
OUTPUT_FOLDER = Path("outputs")
OUTPUT_FILE = OUTPUT_FOLDER / "road_gps_points.csv"

OUTPUT_FOLDER.mkdir(exist_ok=True)

all_roads = []

for file in sorted(SURVEY_FOLDER.glob("*.csv")):
    match = re.match(r"(B\d{3})", file.stem, re.IGNORECASE)

    if not match:
        print(f"Skipping unknown filename: {file.name}")
        continue

    road_id = match.group(1).upper()

    df = pd.read_csv(
        file,
        usecols=[
            "Section",
            "Chainage__km_",
            "Latitude__deg_",
            "Longitude__deg_",
        ],
    )

    df = df.rename(
        columns={
            "Chainage__km_": "chainage_km",
            "Latitude__deg_": "latitude",
            "Longitude__deg_": "longitude",
        }
    )

    for col in ["chainage_km", "latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove survey setup sections such as LEADIN.
    # Retain only sections belonging to this road.
    section = df["Section"].fillna("").astype(str).str.upper()
    road_section_prefix = road_id + "_"

    df = df[section.str.startswith(road_section_prefix)].copy()

    # Basic coordinate and chainage validation.
    df = df[
        df["latitude"].between(5, 10)
        & df["longitude"].between(79, 82)
        & df["chainage_km"].notna()
    ].copy()

    df["road_id"] = road_id
    all_roads.append(
        df[["road_id", "chainage_km", "latitude", "longitude"]]
    )

if not all_roads:
    raise ValueError("No usable road GPS records found.")

combined = pd.concat(all_roads, ignore_index=True)

# Combine left/right observations at the same road chainage.
# Median reduces the effect of small GPS differences.
road_points = (
    combined.groupby(["road_id", "chainage_km"], as_index=False)
    .agg(
        latitude=("latitude", "median"),
        longitude=("longitude", "median"),
    )
    .sort_values(["road_id", "chainage_km"])
)

road_points.to_csv(OUTPUT_FILE, index=False)

print("\nROAD GPS PREPARATION COMPLETED")
print("Output file:", OUTPUT_FILE)
print("Total unique road-chainage points:", len(road_points))
print("\nPOINTS PER ROAD:")
print(road_points.groupby("road_id").size().to_string())
print("\nFIRST 5 ROWS:")
print(road_points.head().to_string(index=False))
