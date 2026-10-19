
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
import json
import time

import pandas as pd


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

INPUT_FILE = Path("outputs/road_gps_points.csv")
OUTPUT_FILE = Path("outputs/nearby_important_locations.csv")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Approximately 1.3 km latitude margin.
# This is only for collecting candidate locations.
# Actual road-to-place distances will be calculated later.
SEARCH_MARGIN_DEGREES = 0.012


# --------------------------------------------------
# LOAD ROAD GPS DATA
# --------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Missing input file: {INPUT_FILE}"
    )

roads = pd.read_csv(INPUT_FILE)

required_columns = {
    "road_id",
    "latitude",
    "longitude",
}

missing = required_columns - set(roads.columns)

if missing:
    raise ValueError(
        f"Missing columns in GPS file: {sorted(missing)}"
    )

print("ROAD GPS DATA LOADED")
print("Roads:", sorted(roads["road_id"].unique()))
print("Total GPS points:", len(roads))


# --------------------------------------------------
# DOWNLOAD IMPORTANT LOCATIONS
# --------------------------------------------------

all_locations = []

for road_id, road_points in roads.groupby("road_id"):

    print(f"\nSearching important locations near {road_id}...")

    south = road_points["latitude"].min() - SEARCH_MARGIN_DEGREES
    north = road_points["latitude"].max() + SEARCH_MARGIN_DEGREES

    west = road_points["longitude"].min() - SEARCH_MARGIN_DEGREES
    east = road_points["longitude"].max() + SEARCH_MARGIN_DEGREES

    # OpenStreetMap amenities:
    # hospital, school, police, fire_station
    query = f"""
    [out:json][timeout:120];
    (
      nwr["amenity"~"^(hospital|school|police|fire_station)$"]
      ({south},{west},{north},{east});
    );
    out center;
    """

    request_data = urlencode({
        "data": query
    }).encode("utf-8")

    request = Request(
        OVERPASS_URL,
        data=request_data,
        headers={
            "User-Agent": "AcademicRoadPriorityResearch/1.0"
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=180) as response:
            result = json.load(response)

    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(
            f"OpenStreetMap request failed for {road_id}. "
            f"Please try again later. Details: {error}"
        ) from error

    elements = result.get("elements", [])

    count = 0

    for element in elements:

        tags = element.get("tags", {})

        # Nodes have direct coordinates.
        # Ways/relations may have a calculated center.
        latitude = element.get("lat")
        longitude = element.get("lon")

        if latitude is None or longitude is None:
            center = element.get("center", {})
            latitude = center.get("lat")
            longitude = center.get("lon")

        if latitude is None or longitude is None:
            continue

        all_locations.append({
            "road_id": road_id,
            "osm_type": element.get("type"),
            "osm_id": element.get("id"),
            "location_name": tags.get("name", ""),
            "amenity_type": tags.get("amenity", ""),
            "latitude": latitude,
            "longitude": longitude,
        })

        count += 1

    print(f"Candidate locations found: {count}")

    # Avoid sending many requests too quickly.
    time.sleep(3)


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

columns = [
    "road_id",
    "osm_type",
    "osm_id",
    "location_name",
    "amenity_type",
    "latitude",
    "longitude",
]

locations = pd.DataFrame(
    all_locations,
    columns=columns,
)

# Remove duplicate OSM objects for each road.
locations = locations.drop_duplicates(
    subset=["road_id", "osm_type", "osm_id"]
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

locations.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n" + "=" * 55)
print("IMPORTANT LOCATIONS COLLECTION COMPLETED")
print("=" * 55)

print("Output file:", OUTPUT_FILE)
print("Total candidate road-location records:", len(locations))

if not locations.empty:

    print("\nLOCATIONS BY TYPE:")
    print(
        locations["amenity_type"]
        .value_counts()
        .to_string()
    )

    print("\nLOCATIONS BY ROAD:")
    print(
        locations.groupby("road_id")
        .size()
        .to_string()
    )

    print("\nFIRST 5 ROWS:")
    print(
        locations.head(5).to_string(index=False)
    )

else:
    print("No locations returned by the map service.")
