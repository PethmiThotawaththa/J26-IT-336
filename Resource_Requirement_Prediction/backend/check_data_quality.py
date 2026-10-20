
from pathlib import Path
import pandas as pd
ROOT = Path(r"D:\Y4S1\RP\PP1\RESOURCES")

# Use the actual research project folder.
PROJECT = Path.cwd()
PROCESSED = PROJECT / "data" / "processed"

MAINTENANCE_FILE = PROCESSED / "maintenance_source_audit.csv"
TRAFFIC_FILE = PROCESSED / "traffic_clean.csv"
WEATHER_FILE = ROOT / "Whether.csv"


def require_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")


def print_section(title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


def show_missing_values(df, dataset_name):
    print(f"\n{dataset_name} — missing values")
    missing = df.isna().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("No missing values detected.")
    else:
        print(missing.to_string())


def show_numeric_summary(df, columns, dataset_name):
    available = [
        column
        for column in columns
        if column in df.columns
    ]

    if not available:
        print(f"\nNo requested numeric columns found in {dataset_name}.")
        return

    numeric_df = df[available].copy()

    for column in available:
        numeric_df[column] = pd.to_numeric(
            numeric_df[column],
            errors="coerce",
        )

    print(f"\n{dataset_name} — numeric summary")
    print(numeric_df.describe().round(3).to_string())


def main():
    for path in [
        MAINTENANCE_FILE,
        TRAFFIC_FILE,
        WEATHER_FILE,
    ]:
        require_file(path)

    # ---------------------------------------------------------
    # 1. MAINTENANCE DATA
    # ---------------------------------------------------------
    maintenance = pd.read_csv(
        MAINTENANCE_FILE,
        dtype={"RoadID_Raw": "string"},
    )

    required_maintenance = [
        "RoadID_Raw",
        "Inspection_Date_Raw",
        "Inspection_Date_Parsed",
        "Item_Code",
        "Units",
        "Quantity",
        "Total_Amount_Rs",
        "Data_Status",
        "Date_Parse_Status",
    ]

    missing_columns = [
        column
        for column in required_maintenance
        if column not in maintenance.columns
    ]

    if missing_columns:
        raise ValueError(
            "Maintenance dataset is missing columns: "
            + ", ".join(missing_columns)
        )

    maintenance["Inspection_Date"] = pd.to_datetime(
        maintenance["Inspection_Date_Parsed"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    maintenance["Quantity"] = pd.to_numeric(
        maintenance["Quantity"],
        errors="coerce",
    )

    maintenance["Total_Amount_Rs"] = pd.to_numeric(
        maintenance["Total_Amount_Rs"],
        errors="coerce",
    )

    # ---------------------------------------------------------
    # 2. TRAFFIC DATA
    # ---------------------------------------------------------
    traffic = pd.read_csv(TRAFFIC_FILE)

    if "Traffic_Date" not in traffic.columns:
        raise ValueError(
            "Traffic dataset is missing Traffic_Date."
        )

    if "RoadID" not in traffic.columns:
        raise ValueError(
            "Traffic dataset is missing RoadID."
        )

    traffic["Traffic_Date"] = pd.to_datetime(
        traffic["Traffic_Date"],
        errors="coerce",
    )

    # Convert available traffic measurements to numeric values.
    traffic_numeric_candidates = [
        "Chainage_KM",
        "Total_Vehicles",
        "Count_Hours",
    ]

    for column in traffic_numeric_candidates:
        if column in traffic.columns:
            traffic[column] = pd.to_numeric(
                traffic[column],
                errors="coerce",
            )

    # ---------------------------------------------------------
    # 3. WEATHER DATA
    # ---------------------------------------------------------
    weather = pd.read_csv(WEATHER_FILE)

    required_weather = ["year", "month", "day"]
    missing_weather = [
        column
        for column in required_weather
        if column not in weather.columns
    ]

    if missing_weather:
        raise ValueError(
            "Weather dataset is missing columns: "
            + ", ".join(missing_weather)
        )

    weather["Weather_Date"] = pd.to_datetime(
        {
            "year": pd.to_numeric(
                weather["year"], errors="coerce"
            ),
            "month": pd.to_numeric(
                weather["month"], errors="coerce"
            ),
            "day": pd.to_numeric(
                weather["day"], errors="coerce"
            ),
        },
        errors="coerce",
    )

    weather_numeric_candidates = [
        "temp",
        "prcp",
        "rhum",
        "wspd",
    ]

    for column in weather_numeric_candidates:
        if column in weather.columns:
            weather[column] = pd.to_numeric(
                weather[column],
                errors="coerce",
            )

    # ---------------------------------------------------------
    # 4. MAINTENANCE QUALITY REPORT
    # ---------------------------------------------------------
    print_section("1. MAINTENANCE DATA QUALITY")

    print(f"Total records: {len(maintenance)}")
    print(
        "Verified parsed dates: "
        f"{maintenance['Inspection_Date'].notna().sum()}"
    )
    print(
        "Invalid or missing parsed dates: "
        f"{maintenance['Inspection_Date'].isna().sum()}"
    )

    valid_maintenance_dates = maintenance[
        "Inspection_Date"
    ].dropna()

    if not valid_maintenance_dates.empty:
        print(
            "Date range: "
            f"{valid_maintenance_dates.min().date()} to "
            f"{valid_maintenance_dates.max().date()}"
        )

    print(
        "Source date convention: DD/MM/YYYY "
        "(confirmed by the source audit)"
    )

    print("\nDate parsing status:")
    print(
        maintenance["Date_Parse_Status"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nData status:")
    print(
        maintenance["Data_Status"]
        .value_counts(dropna=False)
        .to_string()
    )

    show_missing_values(maintenance, "Maintenance")

    print("\nNegative quantities:", (
        maintenance["Quantity"].dropna() < 0
    ).sum())

    print("Zero quantities:", (
        maintenance["Quantity"].dropna() == 0
    ).sum())

    print("Negative amounts:", (
        maintenance["Total_Amount_Rs"].dropna() < 0
    ).sum())

    print(
        "Missing quantity values: "
        f"{maintenance['Quantity'].isna().sum()}"
    )

    print(
        "Missing amount values: "
        f"{maintenance['Total_Amount_Rs'].isna().sum()}"
    )

    print(
        "Distinct item codes: "
        f"{maintenance['Item_Code'].nunique(dropna=True)}"
    )

    print(
        "Distinct item-code/unit combinations: "
        f"{maintenance[['Item_Code', 'Units']].drop_duplicates().shape[0]}"
    )

    show_numeric_summary(
        maintenance,
        ["Quantity", "Total_Amount_Rs"],
        "Maintenance",
    )

    # ---------------------------------------------------------
    # 5. TRAFFIC QUALITY REPORT
    # ---------------------------------------------------------
    print_section("2. TRAFFIC DATA QUALITY")

    print(f"Cleaned traffic records: {len(traffic)}")
    print(
        "Valid traffic dates: "
        f"{traffic['Traffic_Date'].notna().sum()}"
    )
    print(
        "Invalid or missing traffic dates: "
        f"{traffic['Traffic_Date'].isna().sum()}"
    )

    valid_traffic_dates = traffic["Traffic_Date"].dropna()

    if not valid_traffic_dates.empty:
        print(
            "Date range: "
            f"{valid_traffic_dates.min().date()} to "
            f"{valid_traffic_dates.max().date()}"
        )

    print(
        "Distinct road IDs: "
        f"{traffic['RoadID'].nunique(dropna=True)}"
    )

    if "Source_Excel_Row" in traffic.columns:
        print(
            "Duplicate source Excel row references: "
            f"{traffic['Source_Excel_Row'].duplicated().sum()}"
        )

    show_missing_values(traffic, "Traffic")

    show_numeric_summary(
        traffic,
        traffic_numeric_candidates,
        "Traffic",
    )

    for column in [
        "Chainage_KM",
        "Total_Vehicles",
        "Count_Hours",
    ]:
        if column in traffic.columns:
            values = traffic[column].dropna()
            print(
                f"{column} negative values: "
                f"{(values < 0).sum()}"
            )

    # ---------------------------------------------------------
    # 6. WEATHER QUALITY REPORT
    # ---------------------------------------------------------
    print_section("3. WEATHER DATA QUALITY")

    print(f"Weather records: {len(weather)}")
    print(
        "Valid weather dates: "
        f"{weather['Weather_Date'].notna().sum()}"
    )
    print(
        "Invalid or missing weather dates: "
        f"{weather['Weather_Date'].isna().sum()}"
    )

    valid_weather_dates = weather["Weather_Date"].dropna()

    if not valid_weather_dates.empty:
        print(
            "Date range: "
            f"{valid_weather_dates.min().date()} to "
            f"{valid_weather_dates.max().date()}"
        )

    print(
        "Duplicate weather dates: "
        f"{weather['Weather_Date'].duplicated().sum()}"
    )

    show_missing_values(weather, "Weather")

    show_numeric_summary(
        weather,
        weather_numeric_candidates,
        "Weather",
    )

    for column in weather_numeric_candidates:
        if column in weather.columns:
            values = weather[column].dropna()
            print(
                f"{column} negative values: "
                f"{(values < 0).sum()}"
            )

    # ---------------------------------------------------------
    # 7. TEMPORAL ALIGNMENT CHECK
    # ---------------------------------------------------------
    print_section("4. TEMPORAL ALIGNMENT CHECK")

    if (
        not valid_maintenance_dates.empty
        and not valid_traffic_dates.empty
    ):
        start_date = valid_maintenance_dates.min()
        end_date = valid_maintenance_dates.max()

        aligned_traffic = traffic[
            traffic["Traffic_Date"].between(
                start_date,
                end_date,
            )
        ]

        print(
            "Maintenance inspection period: "
            f"{start_date.date()} to {end_date.date()}"
        )

        print(
            "Traffic records within this period: "
            f"{len(aligned_traffic)}"
        )

        if aligned_traffic.empty:
            print(
                "WARNING: Traffic dates do not overlap with "
                "the maintenance inspection period."
            )

    if (
        not valid_maintenance_dates.empty
        and not valid_weather_dates.empty
    ):
        start_date = valid_maintenance_dates.min()
        end_date = valid_maintenance_dates.max()

        aligned_weather = weather[
            weather["Weather_Date"].between(
                start_date,
                end_date,
            )
        ]

        print(
            "Weather records within the maintenance period: "
            f"{len(aligned_weather)}"
        )

        print(
            "Note: matching dates do not alone establish a valid "
            "weather-to-road-task relationship."
        )

    # ---------------------------------------------------------
    # 8. RESEARCH DATA LIMITATIONS
    # ---------------------------------------------------------
    print_section("5. RESEARCH DATA LIMITATIONS")

    print(
        "1. Maintenance quantities and costs are budget estimates; "
        "they are not verified actual resource consumption."
    )
    print(
        "2. Traffic data has no records within the maintenance "
        "inspection date range."
    )
    print(
        "3. Weather data contains missing precipitation values."
    )
    print(
        "4. Matching road IDs and dates does not prove matching "
        "road chainage or task-level conditions."
    )
    print(
        "5. HSR-based estimates must be distinguished from actual "
        "consumption and simulated training targets."
    )
    print(
        "6. Quality checks do not establish predictive model "
        "accuracy or prove that a dataset is representative."
    )

    print_section("DATA QUALITY CHECK COMPLETED")


if __name__ == "__main__":
    main()
