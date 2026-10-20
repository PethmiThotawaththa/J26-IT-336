
from pathlib import Path
import pandas as pd

ROOT = Path(r"D:\Y4S1\RP\PP1\RESOURCES")
SOURCE_FILE = ROOT / "Forecasted routine maintenance budget 2026.xlsx"
OUTPUT_DIR = Path.cwd() / "outputs"

REQUIRED_COLUMNS = [
    "RoadID",
    "Inspection date",
    "Item Code",
    "Rate (Rs.)",
    "Units",
    "Quantity",
    "Total Amount (Rs.)",
]


def print_section(title):
    print("\n" + "=" * 75)
    print(title)
    print("=" * 75)


def main():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Original maintenance workbook not found: {SOURCE_FILE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read the original source without modifying it.
    df = pd.read_excel(
        SOURCE_FILE,
        sheet_name="Budget",
    )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The workbook is missing required columns: "
            + ", ".join(missing_columns)
        )

    # Preserve source values and create normalized analysis columns.
    df["RoadID_Normalized"] = (
        df["RoadID"]
        .astype("string")
        .str.strip()
        .str.upper()
        .str.replace(r"^B0*(\d+)$", r"B\1", regex=True)
    )

    df["Item_Code_Normalized"] = (
        df["Item Code"].astype("string").str.strip()
    )

    df["Units_Normalized"] = (
        df["Units"].astype("string").str.strip()
    )

    # The source audit confirmed DD/MM/YYYY.
    df["Inspection_Date_Parsed"] = pd.to_datetime(
        df["Inspection date"],
        format="%d/%m/%Y %I:%M:%S %p",
        errors="coerce",
    )

    numeric_columns = [
        "Rate (Rs.)",
        "Quantity",
        "Total Amount (Rs.)",
        "StartChainage(m)",
        "EndChainage(m)",
        "From (m)",
        "To (m)",
        "Length (m)",
        "Count",
        "Width (m)",
        "Depth (m)",
        "Times per year (Frequency)",
        "Density (kg/m3)",
        "Weight (m.ton)",
        "Area (sqm)",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    print_section("1. SOURCE WORKBOOK OVERVIEW")
    print(f"Source file: {SOURCE_FILE}")
    print(f"Sheet: Budget")
    print(f"Total records: {len(df)}")
    print(
        "Unique normalized road IDs: "
        f"{df['RoadID_Normalized'].nunique(dropna=True)}"
    )
    print(
        "Distinct item codes: "
        f"{df['Item_Code_Normalized'].nunique(dropna=True)}"
    )
    print(
        "Distinct item-code/unit combinations: "
        f"{df[['Item_Code_Normalized', 'Units_Normalized']].drop_duplicates().shape[0]}"
    )
    print(
        "Valid inspection dates: "
        f"{df['Inspection_Date_Parsed'].notna().sum()}"
    )

    valid_dates = df["Inspection_Date_Parsed"].dropna()

    if not valid_dates.empty:
        print(
            "Inspection date range: "
            f"{valid_dates.min().date()} to "
            f"{valid_dates.max().date()}"
        )

    print_section("2. SUMMARY BY MAINTENANCE ITEM CODE AND UNIT")

    summary = (
        df.groupby(
            ["Item_Code_Normalized", "Units_Normalized"],
            dropna=False,
        )
        .agg(
            record_count=("RoadID", "size"),
            road_count=("RoadID_Normalized", "nunique"),
            total_quantity=("Quantity", "sum"),
            total_amount_rs=("Total Amount (Rs.)", "sum"),
            average_rate_rs=("Rate (Rs.)", "mean"),
        )
        .reset_index()
        .rename(
            columns={
                "Item_Code_Normalized": "Item_Code",
                "Units_Normalized": "Units",
            }
        )
        .sort_values(
            ["Item_Code", "Units"],
            na_position="last",
        )
    )

    print(summary.to_string(index=False))

    print_section("3. AVAILABLE MEASUREMENT FIELDS")

    measurement_columns = [
        "StartChainage(m)",
        "EndChainage(m)",
        "From (m)",
        "To (m)",
        "Length (m)",
        "Count",
        "Width (m)",
        "Depth (m)",
        "Times per year (Frequency)",
        "Density (kg/m3)",
        "Weight (m.ton)",
        "Area (sqm)",
    ]

    available_measurements = [
        column
        for column in measurement_columns
        if column in df.columns
    ]

    measurement_summary = []

    for column in available_measurements:
        values = df[column]

        measurement_summary.append(
            {
                "Field": column,
                "Non_Missing_Count": int(values.notna().sum()),
                "Zero_Count": int((values == 0).sum()),
                "Positive_Count": int((values > 0).sum()),
                "Negative_Count": int((values < 0).sum()),
                "Unique_Values": int(values.nunique(dropna=True)),
            }
        )

    measurement_df = pd.DataFrame(measurement_summary)

    print(measurement_df.to_string(index=False))

    print_section("4. EXAMPLE SOURCE ROWS BY ITEM CODE")

    for item_code in sorted(
        df["Item_Code_Normalized"].dropna().unique(),
        key=lambda value: (
            not str(value).isdigit(),
            int(value) if str(value).isdigit() else str(value),
        ),
    ):
        matching = df[
            df["Item_Code_Normalized"] == item_code
        ]

        print(f"\nItem code: {item_code}")
        print(
            matching[
                [
                    "RoadID",
                    "Inspection date",
                    "Item Code",
                    "Rate (Rs.)",
                    "Units",
                    "Quantity",
                    "Total Amount (Rs.)",
                    "From (m)",
                    "To (m)",
                    "Length (m)",
                    "Width (m)",
                    "Depth (m)",
                    "Times per year (Frequency)",
                    "Weight (m.ton)",
                    "Area (sqm)",
                ]
            ]
            .head(3)
            .to_string(index=False)
        )

    print_section("5. SOURCE DATA LIMITATIONS")

    print(
        "- The workbook is a forecasted routine maintenance budget."
    )
    print(
        "- Quantity and total amount do not establish actual resource "
        "consumption such as labour person-days or equipment hours."
    )
    print(
        "- Measurement fields may be zero or blank where they are "
        "not applicable or were not recorded."
    )
    print(
        "- Item codes must be interpreted using their authoritative "
        "maintenance descriptions or source documentation."
    )
    print(
        "- Do not infer an HSR mapping solely from a matching unit."
    )

    # Save auditable outputs without overwriting the source workbook.
    summary_path = OUTPUT_DIR / "maintenance_item_summary.csv"
    measurement_path = OUTPUT_DIR / "maintenance_measurement_summary.csv"

    summary.to_csv(summary_path, index=False)
    measurement_df.to_csv(measurement_path, index=False)

    print_section("6. OUTPUT FILES")
    print(f"Item summary: {summary_path}")
    print(f"Measurement summary: {measurement_path}")
    print("Original source workbook was not modified.")
    print("\nMAINTENANCE ITEM SUMMARY COMPLETED")


if __name__ == "__main__":
    main()
