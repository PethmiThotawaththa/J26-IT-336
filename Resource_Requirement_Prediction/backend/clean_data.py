
from pathlib import Path
import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_FILE = Path(
    r"D:\Y4S1\RP\PP1\RESOURCES\Forecasted routine maintenance budget 2026.xlsx"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "maintenance_budget_clean.csv"
)


def main():
    # Check whether the source workbook exists
    if not SOURCE_FILE.is_file():
        raise FileNotFoundError(
            f"Workbook not found: {SOURCE_FILE}"
        )

    # Read the Budget worksheet
    df = pd.read_excel(
        SOURCE_FILE,
        sheet_name="Budget"
    )

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Required columns
    required = [
        "RoadID",
        "Item Code",
        "Units",
        "Quantity",
        "Rate (Rs.)",
        "Total Amount (Rs.)"
    ]

    # Check required columns
    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # Normalize road IDs.
    # Example: B0047 -> B047
    #          B0174 -> B174
    df["RoadID"] = (
        df["RoadID"]
        .astype("string")
        .str.strip()
        .str.upper()
        .str.replace(
            r"^B0*(\d+)$",
            lambda match: "B" + match.group(1).zfill(3),
            regex=True
        )
    )

    # Convert numeric columns
    numeric_columns = [
        "Item Code",
        "Quantity",
        "Rate (Rs.)",
        "Total Amount (Rs.)"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Standardize units
    df["Units"] = (
        df["Units"]
        .astype("string")
        .str.strip()
    )

    # Preserve the source-data status.
    # These are budget estimates, not actual resource usage.
    df["Data_Status"] = "ESTIMATE"
    df["Source_File"] = SOURCE_FILE.name
    df["Source_Sheet"] = "Budget"
    df["Validation_Issue"] = ""

    # Validate required values
    invalid = df[required].isna().any(axis=1)

    df.loc[invalid, "Validation_Issue"] += (
        "Missing or invalid key value; "
    )

    # Check for negative values
    df.loc[
        df["Quantity"] < 0,
        "Validation_Issue"
    ] += "Negative quantity; "

    df.loc[
        df["Rate (Rs.)"] < 0,
        "Validation_Issue"
    ] += "Negative rate; "

    df.loc[
        df["Total Amount (Rs.)"] < 0,
        "Validation_Issue"
    ] += "Negative total amount; "

    # Compare quantity x rate with the reported total.
    # A tolerance of Rs. 1 is allowed for rounding.
    calculated_total = (
        df["Quantity"] * df["Rate (Rs.)"]
    )

    mismatch = (
        calculated_total - df["Total Amount (Rs.)"]
    ).abs() > 1.0

    df.loc[
        mismatch,
        "Validation_Issue"
    ] += "Quantity x rate differs from total; "

    # Create output directory if needed
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save cleaned data
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # Display summary
    print("Cleaning completed successfully.")
    print(f"Rows processed: {len(df)}")
    print(f"Unique roads: {df['RoadID'].nunique()}")
    print(
        f"Unique item codes: "
        f"{df['Item Code'].nunique()}"
    )
    print(
        "Rows with validation issues: "
        f"{df['Validation_Issue'].ne('').sum()}"
    )
    print(f"Output saved to: {OUTPUT_FILE}")
    print(
        "Source records are labelled ESTIMATE, "
        "not actual resource consumption."
    )


if __name__ == "__main__":
    main()
