
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

ROAD_FILE = Path("outputs/road_gps_points.csv")
LOCATIONS_FILE = Path("outputs/nearby_important_locations.csv")
OUTPUT_FILE = Path("outputs/road_nearby_location_features.csv")

EARTH_RADIUS_M = 6371000.0
NEARBY_RADIUS_M = 500.0

AMENITY_TYPES = [
    "hospital",
    "school",
    "police",
    "fire_station",
]


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

roads = pd.read_csv(ROAD_FILE)
locations = pd.read_csv(LOCATIONS_FILE)

print("Road GPS points:", len(roads))
print("Candidate location records:", len(locations))

# An OSM object may appear in searches for multiple roads.
# Keep each OSM object only once in the master locations table.
locations = locations.drop_duplicates(
    subset=["osm_type", "osm_id"]
).copy()

for column in ["latitude", "longitude"]:
    roads[column] = pd.to_numeric(
        roads[column], errors="coerce"
    )
    locations[column] = pd.to_numeric(
        locations[column], errors="coerce"
    )

roads = roads.dropna(
    subset=["road_id", "latitude", "longitude"]
)

locations = locations.dropna(
    subset=["latitude", "longitude", "amenity_type"]
)

locations = locations[
    locations["amenity_type"].isin(AMENITY_TYPES)
].copy()

print("Unique OSM location objects:", len(locations))


# --------------------------------------------------
# CALCULATE DISTANCE FROM EACH LOCATION
# TO THE NEAREST GPS POINT ON EACH ROAD
# --------------------------------------------------

results = []

for road_id, road_points in roads.groupby("road_id"):

    print(f"\nProcessing {road_id}...")

    road_coordinates = np.radians(
        road_points[["latitude", "longitude"]].to_numpy()
    )

    # Haversine BallTree calculates great-circle distances.
    road_tree = BallTree(
        road_coordinates,
        metric="haversine"
    )

    row = {
        "road_id": road_id,
        "nearby_hospital_count_500m": 0,
        "nearby_school_count_500m": 0,
        "nearby_police_count_500m": 0,
        "nearby_fire_station_count_500m": 0,
        "nearest_hospital_distance_m": np.nan,
        "nearest_school_distance_m": np.nan,
        "nearest_police_distance_m": np.nan,
        "nearest_fire_station_distance_m": np.nan,
    }

    for amenity in AMENITY_TYPES:

        selected = locations[
            locations["amenity_type"] == amenity
        ]

        if selected.empty:
            continue

        place_coordinates = np.radians(
            selected[["latitude", "longitude"]].to_numpy()
        )

        distances_radians, _ = road_tree.query(
            place_coordinates,
            k=1
        )

        distances_m = (
            distances_radians[:, 0] * EARTH_RADIUS_M
        )

        count = int(
            np.sum(distances_m <= NEARBY_RADIUS_M)
        )

        nearest = float(np.min(distances_m))

        row[f"nearby_{amenity}_count_500m"] = count
        row[f"nearest_{amenity}_distance_m"] = round(
            nearest, 2
        )

    results.append(row)


# --------------------------------------------------
# SAVE FEATURES
# --------------------------------------------------

features = pd.DataFrame(results).sort_values(
    "road_id"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

features.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("NEARBY IMPORTANT LOCATIONS FEATURES COMPLETED")
print("=" * 60)

print("Output file:", OUTPUT_FILE)

print("\nROAD-LEVEL FEATURES:")
print(features.to_string(index=False))

print(
    "\nNOTE: Distances are approximate straight-line "
    "distances to the nearest sampled road GPS point."
)
