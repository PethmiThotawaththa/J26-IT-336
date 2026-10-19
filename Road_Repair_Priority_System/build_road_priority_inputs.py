
from pathlib import Path
import re
import pandas as pd


# =====================================================
# 1. PROJECT FOLDERS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "datasets"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_ROADS = [
    "B047",
    "B174",
    "B214",
    "B240",
    "B263",
    "B435",
]


# =====================================================
# 2. HELPER FUNCTIONS
# =====================================================

def find_excel_file(start_name):
    matches = sorted(
        file
        for file in DATASETS_DIR.glob("*.xlsx")
        if file.name.lower().startswith(start_name.lower())
        and not file.name.startswith("~$")
    )

    if not matches:
        raise FileNotFoundError(
            f"Excel file not found: {start_name}\n"
            f"Check folder: {DATASETS_DIR}"
        )

    if len(matches) > 1:
        raise ValueError(
            f"Multiple matching Excel files found: "
            f"{[file.name for file in matches]}"
        )

    print(f"Found: {matches[0].name}")
    return matches[0]


def normalize_road_id(value):
    if pd.isna(value):
        return None

    text = re.sub(
        r"\s+",
        "",
        str(value).strip().upper()
    )

    match = re.fullmatch(r"B0*(\d+)", text)

    if match:
        return f"B{int(match.group(1)):03d}"

    return None


def clean_columns(dataframe):
    dataframe = dataframe.copy()
    dataframe.columns = (
        dataframe.columns.astype(str).str.strip()
    )
    return dataframe


def require_columns(dataframe, columns, source):
    missing = [
        column
        for column in columns
        if column not in dataframe.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in {source}: {missing}\n"
            f"Available columns: {list(dataframe.columns)}"
        )


# =====================================================
# 3. FIND INPUT FILES
# =====================================================

print("\nFinding RDA datasets...")

traffic_file = find_excel_file(
    "Traffic Data of Roads"
)

budget_file = find_excel_file(
    "Forecasted routine maintenance budget 2026"
)

weather_file = DATASETS_DIR / "Whether.csv"

if not weather_file.exists():
    raise FileNotFoundError(
        f"Weather CSV not found: {weather_file}"
    )

print(f"Found: {weather_file.name}")


# =====================================================
# 4. PROCESS TRAFFIC DATA
# =====================================================

print("\nProcessing Traffic Data...")

traffic = pd.read_excel(
    traffic_file,
    sheet_name="Traffic Counts"
)

traffic = clean_columns(traffic)

require_columns(
    traffic,
    [
        "ROUTE NO",
        "TOTAL NO.OF VEH.",
        "HRS OF COUNT",
    ],
    "Traffic Counts"
)

traffic["road_id"] = traffic["ROUTE NO"].apply(
    normalize_road_id
)

traffic["vehicle_count"] = pd.to_numeric(
    traffic["TOTAL NO.OF VEH."],
    errors="coerce"
)

traffic["count_hours"] = pd.to_numeric(
    traffic["HRS OF COUNT"],
    errors="coerce"
)

traffic = traffic[
    traffic["road_id"].isin(TARGET_ROADS)
    & (traffic["vehicle_count"] >= 0)
    & (traffic["count_hours"] > 0)
].copy()

traffic["vehicles_per_hour"] = (
    traffic["vehicle_count"] / traffic["count_hours"]
)

traffic_summary = (
    traffic.groupby("road_id")
    .agg(
        traffic_observation_count=(
            "vehicles_per_hour",
            "count"
        ),
        traffic_mean_vehicles_per_hour=(
            "vehicles_per_hour",
            "mean"
        ),
        traffic_min_vehicles_per_hour=(
            "vehicles_per_hour",
            "min"
        ),
        traffic_max_vehicles_per_hour=(
            "vehicles_per_hour",
            "max"
        )
    )
    .reset_index()
)


# =====================================================
# 5. PROCESS FORECASTED BUDGET DATA
# =====================================================

print("Processing Forecasted Budget Data...")

budget = pd.read_excel(
    budget_file,
    sheet_name="Budget"
)

budget = clean_columns(budget)

require_columns(
    budget,
    [
        "RoadID",
        "Total Amount (Rs.)",
    ],
    "Budget"
)

budget["road_id"] = budget["RoadID"].apply(
    normalize_road_id
)

budget["amount_lkr"] = pd.to_numeric(
    budget["Total Amount (Rs.)"],
    errors="coerce"
)

budget = budget[
    budget["road_id"].isin(TARGET_ROADS)
    & budget["amount_lkr"].notna()
].copy()

budget_summary = (
    budget.groupby("road_id")
    .agg(
        forecast_2026_budget_lkr=(
            "amount_lkr",
            "sum"
        ),
        forecast_2026_budget_item_count=(
            "amount_lkr",
            "count"
        )
    )
    .reset_index()
)


# =====================================================
# 6. PROCESS ROAD INFORMATION
# =====================================================

print("Processing Road Information...")

roads = pd.read_excel(
    budget_file,
    sheet_name="Road Names and length"
)

roads = clean_columns(roads)

require_columns(
    roads,
    [
        "ROUTE No.",
        "ROAD NAME",
        "Total Length (km)",
    ],
    "Road Names and length"
)

roads["road_id"] = roads["ROUTE No."].apply(
    normalize_road_id
)

roads = roads.rename(
    columns={
        "ROAD NAME": "road_name",
        "Total Length (km)": "road_length_km",
    }
)

roads["road_length_km"] = pd.to_numeric(
    roads["road_length_km"],
    errors="coerce"
)

roads = (
    roads[
        roads["road_id"].isin(TARGET_ROADS)
    ][
        [
            "road_id",
            "road_name",
            "road_length_km",
        ]
    ]
    .drop_duplicates(subset=["road_id"])
)


# =====================================================
# 7. PROCESS COLOMBO WEATHER DATA
# =====================================================

print("Processing Colombo Weather Data...")

weather = pd.read_csv(weather_file)
weather = clean_columns(weather)

require_columns(
    weather,
    [
        "year",
        "month",
        "day",
        "temp",
        "rhum",
        "prcp",
        "wspd",
    ],
    "Whether.csv"
)

# Convert date fields into actual dates.
weather["date"] = pd.to_datetime(
    weather[["year", "month", "day"]],
    errors="coerce"
)

# Use only 2025 weather records.
weather = weather[
    weather["date"].dt.year == 2025
].copy()

# Ensure one weather observation per date.
duplicate_dates = weather["date"].duplicated().sum()

if duplicate_dates > 0:
    raise ValueError(
        f"Weather file contains {duplicate_dates} "
        "duplicate dates. Please inspect the CSV."
    )

# Convert weather values into numeric format.
weather_columns = [
    "temp",
    "rhum",
    "prcp",
    "wspd",
]

for column in weather_columns:
    weather[column] = pd.to_numeric(
        weather[column],
        errors="coerce"
    )

if weather.empty:
    raise ValueError(
        "No valid 2025 weather records found."
    )

# Calculate district-level annual weather features.
weather_features = {
    "weather_year": 2025,
    "weather_observation_days": len(weather),
    "colombo_2025_avg_temperature_c": (
        weather["temp"].mean()
    ),
    "colombo_2025_avg_humidity_pct": (
        weather["rhum"].mean()
    ),
    "colombo_2025_total_rainfall_mm": (
        weather["prcp"].sum(min_count=1)
    ),
    "colombo_2025_rainy_days": (
        int((weather["prcp"] > 0).sum())
    ),
    "colombo_2025_avg_wind_speed": (
        weather["wspd"].mean()
    ),
}

print(
    "Weather observation days:",
    weather_features["weather_observation_days"]
)

print(
    "2025 total rainfall (mm):",
    round(
        weather_features[
            "colombo_2025_total_rainfall_mm"
        ],
        2
    )
)


# =====================================================
# 8. COMBINE ALL ROAD-LEVEL FEATURES
# =====================================================

print("\nCombining Road-Level Data...")

# Start with the six target roads.
dataset = pd.DataFrame(
    {"road_id": TARGET_ROADS}
)

dataset = dataset.merge(
    roads,
    on="road_id",
    how="left"
)

dataset = dataset.merge(
    traffic_summary,
    on="road_id",
    how="left"
)

dataset = dataset.merge(
    budget_summary,
    on="road_id",
    how="left"
)

# All six roads are in Colombo District.
dataset["district"] = "Colombo"

# Weather is district-level data.
# Therefore the same 2025 weather summary applies
# to all six Colombo District roads.
for feature_name, feature_value in (
    weather_features.items()
):
    dataset[feature_name] = feature_value

dataset["weather_scope"] = (
    "Colombo district-level shared weather"
)

dataset["budget_data_type"] = (
    "Forecasted routine maintenance budget 2026"
)


# =====================================================
# 9. KEEP UNKNOWN INFORMATION EMPTY
# =====================================================

# Damage information is not available yet.
dataset["road_condition_score"] = pd.NA
dataset["damage_count"] = pd.NA
dataset["damage_severity_summary"] = pd.NA

# Supervised learning requires genuine labels.
# Do not invent priority labels.
dataset["priority_label"] = pd.NA


# =====================================================
# 10. ROUND NUMERIC FEATURES
# =====================================================

numeric_columns = [
    "traffic_mean_vehicles_per_hour",
    "traffic_min_vehicles_per_hour",
    "traffic_max_vehicles_per_hour",
    "forecast_2026_budget_lkr",
    "colombo_2025_avg_temperature_c",
    "colombo_2025_avg_humidity_pct",
    "colombo_2025_total_rainfall_mm",
    "colombo_2025_avg_wind_speed",
]

dataset[numeric_columns] = (
    dataset[numeric_columns].round(2)
)

dataset = dataset.sort_values(
    "road_id"
).reset_index(drop=True)


# =====================================================
# 11. SAVE FINAL PREPARED DATASET
# =====================================================

output_file = (
    OUTPUT_DIR / "road_priority_inputs_unlabelled.csv"
)

dataset.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


# =====================================================
# 12. DISPLAY RESULTS
# =====================================================

print("\n" + "=" * 58)
print("ROAD PRIORITY DATASET PREPARATION COMPLETED")
print("=" * 58)

print("\nOutput file:", output_file)
print("Number of roads:", len(dataset))

print("\nRoad IDs:")
print(dataset["road_id"].tolist())

print("\nDataset Preview:")

preview_columns = [
    "road_id",
    "road_name",
    "traffic_mean_vehicles_per_hour",
    "forecast_2026_budget_lkr",
    "colombo_2025_total_rainfall_mm",
    "priority_label",
]

print(
    dataset[preview_columns].to_string(
        index=False
    )
)

print("\nIMPORTANT NOTES:")
print("- Traffic data included.")
print("- Forecasted budget data included.")
print("- Colombo district weather data included.")
print("- Weather summary is shared by all six roads.")
print("- Priority labels are still unavailable.")
print("- No ML model has been trained.")
print("- Existing ML models have not been modified.")

print("\nDone!")
