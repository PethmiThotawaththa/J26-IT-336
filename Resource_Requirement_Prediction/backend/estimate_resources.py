
from pathlib import Path
import math

import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NORMS_FILE = PROJECT_ROOT / "outputs" / "hsr_resource_norms.csv"
OUTPUT_FILE = PROJECT_ROOT / "outputs" / "resource_estimates.csv"


# --------------------------------------------------
# LOAD AND VALIDATE HSR NORMS
# --------------------------------------------------

def load_norms():
    """Load HSR norms and validate required fields and values."""

    if not NORMS_FILE.exists():
        raise FileNotFoundError(
            f"HSR norms file not found: {NORMS_FILE}"
        )

    try:
        norms = pd.read_csv(NORMS_FILE)
    except (pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError(
            f"Could not read the HSR norms CSV: {error}"
        ) from error

    required_columns = [
        "hsr_item_code",
        "activity",
        "basis_quantity",
        "basis_unit",
        "resource_type",
        "resource_name",
        "resource_quantity",
        "resource_unit",
        "source_pdf_page",
        "data_status",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in norms.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns in HSR norms file: "
            + ", ".join(missing_columns)
        )

    if norms.empty:
        raise ValueError("The HSR norms file contains no records.")

    # Clean text fields.
    text_columns = [
        "hsr_item_code",
        "activity",
        "basis_unit",
        "resource_type",
        "resource_name",
        "resource_unit",
        "data_status",
    ]

    for column in text_columns:
        norms[column] = (
            norms[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    norms["hsr_item_code"] = norms["hsr_item_code"].str.upper()

    # Required text fields must not be blank.
    for column in [
        "hsr_item_code",
        "activity",
        "basis_unit",
        "resource_type",
        "resource_name",
        "resource_unit",
    ]:
        if norms[column].eq("").any():
            raise ValueError(
                f"The HSR norms file contains blank values in '{column}'."
            )

    # Convert numeric fields and reject invalid values.
    for column in ["basis_quantity", "resource_quantity"]:
        norms[column] = pd.to_numeric(
            norms[column],
            errors="coerce"
        )

        if norms[column].isna().any():
            raise ValueError(
                f"Invalid or missing numeric values in '{column}'."
            )

        if not norms[column].map(
            lambda value: math.isfinite(float(value))
        ).all():
            raise ValueError(
                f"Non-finite values are not allowed in '{column}'."
            )

        if (norms[column] < 0).any():
            raise ValueError(
                f"Negative values are not allowed in '{column}'."
            )

    if (norms["basis_quantity"] <= 0).any():
        raise ValueError(
            "Every HSR basis quantity must be greater than zero."
        )

    allowed_statuses = {"ACTUAL", "ESTIMATE", "UNKNOWN", "SIMULATED"}
    invalid_statuses = set(norms["data_status"].str.upper()) - allowed_statuses

    if invalid_statuses:
        raise ValueError(
            "Invalid data status values: "
            + ", ".join(sorted(invalid_statuses))
        )

    norms["data_status"] = norms["data_status"].str.upper()

    return norms


# --------------------------------------------------
# ESTIMATE RESOURCE REQUIREMENTS
# --------------------------------------------------

def estimate_resources(item_code, requested_quantity):
    """
    Estimate resource quantities by proportionally scaling an HSR norm.

    The requested quantity must use the same unit as the HSR basis.
    Results are estimates, not verified actual resource consumption.
    """

    code = str(item_code).strip().upper()

    if not code:
        raise ValueError("HSR item code cannot be blank.")

    try:
        quantity = float(requested_quantity)
    except (TypeError, ValueError):
        raise ValueError(
            "Maintenance quantity must be a valid number."
        ) from None

    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError(
            "Maintenance quantity must be a finite number greater than zero."
        )

    norms = load_norms()

    matches = norms[
        norms["hsr_item_code"] == code
    ].copy()

    if matches.empty:
        available_codes = sorted(
            norms["hsr_item_code"].unique()
        )

        raise ValueError(
            f"Unknown HSR item code '{code}'. Available codes: "
            + ", ".join(available_codes)
        )

    results = []

    for _, norm in matches.iterrows():
        basis_quantity = float(norm["basis_quantity"])
        norm_resource_quantity = float(norm["resource_quantity"])

        # Proportional estimate based on the HSR norm.
        estimated_quantity = (
            norm_resource_quantity
            * quantity
            / basis_quantity
        )

        if not math.isfinite(estimated_quantity):
            raise ValueError(
                "The calculated resource quantity is not finite."
            )

        source_page = str(norm["source_pdf_page"]).strip()

        if source_page and source_page.lower() != "nan":
            source_reference = (
                f"Revised HSR 2026, analysis PDF page {source_page}"
            )
        else:
            source_reference = (
                "Revised HSR 2026; page not recorded"
            )

        notes_value = norm.get("notes", "")
        notes = (
            ""
            if pd.isna(notes_value)
            else str(notes_value).strip()
        )

        results.append({
            "hsr_item_code": code,
            "activity": norm["activity"],
            "requested_quantity": quantity,
            "basis_quantity": basis_quantity,
            "basis_unit": norm["basis_unit"],
            "resource_type": norm["resource_type"],
            "resource_name": norm["resource_name"],
            "norm_resource_quantity": norm_resource_quantity,
            "estimated_resource_quantity": round(
                estimated_quantity, 4
            ),
            "resource_unit": norm["resource_unit"],
            "data_status": "ESTIMATE",
            "source_reference": source_reference,
            "notes": notes,
        })

    return pd.DataFrame(results)


# --------------------------------------------------
# SAVE ESTIMATES WITHOUT DUPLICATE RECORDS
# --------------------------------------------------

def save_estimates(estimates):
    """
    Append new estimates while removing identical duplicate records.

    Different quantities and different resource records are retained.
    """

    if estimates.empty:
        print("No estimates to save.")
        return

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if OUTPUT_FILE.exists():
        try:
            previous = pd.read_csv(OUTPUT_FILE)
            combined = pd.concat(
                [previous, estimates],
                ignore_index=True
            )
        except (pd.errors.ParserError, UnicodeDecodeError) as error:
            raise ValueError(
                f"Could not read the existing estimates file: {error}"
            ) from error
    else:
        combined = estimates.copy()

    duplicate_columns = [
        "hsr_item_code",
        "activity",
        "requested_quantity",
        "basis_quantity",
        "basis_unit",
        "resource_type",
        "resource_name",
        "estimated_resource_quantity",
        "resource_unit",
        "data_status",
        "source_reference",
    ]

    missing_keys = [
        column
        for column in duplicate_columns
        if column not in combined.columns
    ]

    if missing_keys:
        raise ValueError(
            "Cannot check duplicate estimates. Missing columns: "
            + ", ".join(missing_keys)
        )

    combined = combined.drop_duplicates(
        subset=duplicate_columns,
        keep="last"
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Saved estimates to: {OUTPUT_FILE}")
    print(f"Unique estimate records saved: {len(combined)}")


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():
    print("=" * 55)
    print("HSR RESOURCE REQUIREMENT ESTIMATOR")
    print("=" * 55)
    print("Enter an HSR item code and the activity quantity.")
    print("Use the same unit as the HSR norm's basis unit.")
    print("Results are estimates, not actual resource usage.\n")

    try:
        norms = load_norms()

        available_codes = sorted(
            norms["hsr_item_code"].unique()
        )

        print("Available HSR item codes:")
        print(", ".join(available_codes))

        item_code = input(
            "\nEnter HSR item code (e.g. DR1-010): "
        ).strip()

        quantity_text = input(
            "Enter activity quantity in the HSR basis unit: "
        ).strip()

        estimates = estimate_resources(
            item_code,
            quantity_text
        )

        print("\nEstimated resource requirements:")
        print(
            estimates.to_string(index=False)
        )

        save_estimates(estimates)

        print("\nData status: ESTIMATE")
        print(
            "Important: verify the HSR assumptions, units, "
            "and local applicability before operational use."
        )

    except (
        ValueError,
        FileNotFoundError,
        pd.errors.ParserError,
    ) as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()
