
from pathlib import Path
import pandas as pd

ROOT = Path(r"D:\Y4S1\RP\PP1\RESOURCES")
PROJECT = Path.cwd()

PROCESSED = PROJECT / "data" / "processed"
MAINTENANCE_AUDIT = PROCESSED / "maintenance_source_audit.csv"
TRAFFIC_FILE = PROCESSED / "traffic_clean.csv"
WEATHER_FILE = ROOT / "Whether.csv"


def normalize_road_id(value):
    """Normalize road IDs such as B47 and B0047 to B047."""
    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    if value.startswith("B") and value[1:].isdigit():
        return f"B{int(value[1:]):03d}"

    return pd.NA


def require_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")


def main():
    for path in [
        MAINTENANCE_AUDIT,
        TRAFFIC_FILE,
        WEATHER_FILE,
    ]:
        require_file(path)

    # Load the maintenance audit using its actual column names.
    maintenance = pd.read_csv(
        MAINTENANCE_AUDIT,
        dtype={"RoadID_Raw": "string"},
    )

    required_maintenance = {
        "RoadID_Raw",
        "Inspection_Date_Parsed",
        "Item_Code",
        "Units",
        "Quantity",
        "Total_Amount_Rs",
        "Data_Status",
        "Date_Parse_Status",
    }

    missing = required_maintenance - set(maintenance.columns)
    if missing:
        raise ValueError(
            "Maintenance audit is missing columns: "
            + ", ".join(sorted(missing))
        )

    maintenance["RoadID_Normalized"] = (
        maintenance["RoadID_Raw"].apply(normalize_road_id)
    )

    maintenance["Inspection_Date"] = pd.to_datetime(
        maintenance["Inspection_Date_Parsed"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    # Load cleaned traffic records.
    traffic = pd.read_csv(TRAFFIC_FILE)

    for column in ["RoadID", "Traffic_Date"]:
        if column not in traffic.columns:
            raise ValueError(
                f"Traffic dataset is missing required column: {column}"
            )

    traffic["RoadID_Normalized"] = (
        traffic["RoadID"].apply(normalize_road_id)
    )
    traffic["Traffic_Date"] = pd.to_datetime(
        traffic["Traffic_Date"],
        errors="coerce",
    )

    # Load weather data and construct dates.
    weather = pd.read_csv(WEATHER_FILE)

    missing_weather = {"year", "month", "day"} - set(weather.columns)
    if missing_weather:
        raise ValueError(
            "Weather dataset is missing columns: "
            + ", ".join(sorted(missing_weather))
        )

    weather["Weather_Date"] = pd.to_datetime(
        {
            "year": pd.to_numeric(weather["year"], errors="coerce"),
            "month": pd.to_numeric(weather["month"], errors="coerce"),
            "day": pd.to_numeric(weather["day"], errors="coerce"),
        },
        errors="coerce",
    )

    maintenance_dates = maintenance["Inspection_Date"].dropna()
    traffic_dates = traffic["Traffic_Date"].dropna()
    weather_dates = weather["Weather_Date"].dropna()

    print("\n========== DATASET ALIGNMENT AUDIT ==========")

    # 1. Maintenance audit
    print("\n1. MAINTENANCE DATA")
    print(f"Rows: {len(maintenance)}")
    print(
        "Successfully parsed dates: "
        f"{maintenance['Inspection_Date'].notna().sum()}"
    )
    print(
        "Invalid or missing dates: "
        f"{maintenance['Inspection_Date'].isna().sum()}"
    )
    print(
        "Date convention: "
        "DD/MM/YYYY (confirmed by source audit)"
    )

    if not maintenance_dates.empty:
        print(
            f"Date range: {maintenance_dates.min().date()} to "
            f"{maintenance_dates.max().date()}"
        )

    print(
        "Data status counts:\n"
        + maintenance["Data_Status"].value_counts(
            dropna=False
        ).to_string()
    )

    # 2. Road coverage
    maintenance_roads = set(
        maintenance["RoadID_Normalized"].dropna()
    )
    traffic_roads = set(
        traffic["RoadID_Normalized"].dropna()
    )

    print("\n2. ROAD COVERAGE")
    print(f"Maintenance roads: {sorted(maintenance_roads)}")
    print(f"Traffic roads: {sorted(traffic_roads)}")
    print(
        "Road IDs present in both datasets: "
        f"{sorted(maintenance_roads & traffic_roads)}"
    )
    print(
        "Maintenance roads without traffic coverage: "
        f"{sorted(maintenance_roads - traffic_roads)}"
    )
    print(
        "Traffic roads without maintenance coverage: "
        f"{sorted(traffic_roads - maintenance_roads)}"
    )

    # 3. Traffic date alignment
    print("\n3. TRAFFIC DATE ALIGNMENT")
    print(f"Traffic rows: {len(traffic)}")
    print(
        "Valid traffic dates: "
        f"{traffic['Traffic_Date'].notna().sum()}"
    )

    if not traffic_dates.empty:
        print(
            f"Traffic date range: {traffic_dates.min().date()} to "
            f"{traffic_dates.max().date()}"
        )

    if not maintenance_dates.empty:
        start_date = maintenance_dates.min()
        end_date = maintenance_dates.max()

        aligned_traffic = traffic[
            traffic["Traffic_Date"].between(start_date, end_date)
        ]

        print(
            f"Traffic records within maintenance date range "
            f"({start_date.date()} to {end_date.date()}): "
            f"{len(aligned_traffic)}"
        )

        if aligned_traffic.empty:
            print(
                "WARNING: No traffic records fall within the "
                "maintenance inspection date range. Do not treat "
                "these traffic records as date-aligned inspection-time "
                "features."
            )

    # 4. Weather coverage
    print("\n4. WEATHER COVERAGE")
    print(f"Weather rows: {len(weather)}")
    print(f"Valid weather dates: {weather['Weather_Date'].notna().sum()}")

    if not weather_dates.empty:
        print(
            f"Weather date range: {weather_dates.min().date()} to "
            f"{weather_dates.max().date()}"
        )

    print(
        "Duplicate weather dates: "
        f"{weather['Weather_Date'].duplicated().sum()}"
    )

    for column in ["prcp", "prcp_source"]:
        if column in weather.columns:
            print(
                f"Missing values in {column}: "
                f"{weather[column].isna().sum()}"
            )

    # 5. Maintenance item summary
    print("\n5. MAINTENANCE ITEM SUMMARY")

    item_summary = (
        maintenance.groupby(
            ["Item_Code", "Units"],
            dropna=False,
        )
        .agg(
            row_count=("RoadID_Raw", "size"),
            total_quantity=("Quantity", "sum"),
            total_amount_rs=("Total_Amount_Rs", "sum"),
        )
        .reset_index()
        .sort_values("row_count", ascending=False)
    )

    print(
        "Distinct item-code/unit combinations: "
        f"{len(item_summary)}"
    )
    print(item_summary.to_string(index=False))

    # 6. Research limitations
    print("\n6. DATA LIMITATIONS")
    print(
        "- Maintenance quantities and amounts are budget estimates, "
        "not confirmed actual resource consumption."
    )
    print(
        "- Matching road IDs alone does not prove matching location "
        "or chainage."
    )
    print(
        "- Traffic observations outside the maintenance date range "
        "are not date-aligned inspection-time observations."
    )
    print(
        "- Weather date coverage alone does not prove that weather "
        "records are linked to individual maintenance tasks."
    )
    print(
        "- Do not claim that traffic or weather improves prediction "
        "without valid temporal and spatial alignment."
    )

    print("\n========== AUDIT COMPLETED ==========")


if __name__ == "__main__":
    main()
