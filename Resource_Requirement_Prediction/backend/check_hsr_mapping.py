
from pathlib import Path
import pandas as pd

PROJECT = Path.cwd()
PROCESSED = PROJECT / "data" / "processed"
TEMPLATES = PROJECT / "data" / "templates"

MAINTENANCE_FILE = PROCESSED / "maintenance_source_audit.csv"
MAPPING_FILE = TEMPLATES / "hsr_activity_mapping.csv"
HSR_NORMS_FILE = PROJECT / "outputs" / "hsr_resource_norms.csv"


def require_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")


def print_section(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def main():
    # Check required files.
    require_file(MAINTENANCE_FILE)
    require_file(MAPPING_FILE)

    maintenance = pd.read_csv(
        MAINTENANCE_FILE,
        dtype={
            "RoadID_Raw": "string",
            "Item_Code": "string",
            "Units": "string",
        },
    )

    mapping = pd.read_csv(
        MAPPING_FILE,
        dtype={
            "repair_type": "string",
            "hsr_item_code": "string",
            "required_unit": "string",
            "description": "string",
        },
    )

    required_maintenance = {
        "RoadID_Raw",
        "Item_Code",
        "Units",
        "Quantity",
        "Data_Status",
    }

    required_mapping = {
        "repair_type",
        "hsr_item_code",
        "required_unit",
        "description",
    }

    missing_maintenance = required_maintenance - set(
        maintenance.columns
    )
    missing_mapping = required_mapping - set(mapping.columns)

    if missing_maintenance:
        raise ValueError(
            "Maintenance audit is missing columns: "
            + ", ".join(sorted(missing_maintenance))
        )

    if missing_mapping:
        raise ValueError(
            "HSR mapping file is missing columns: "
            + ", ".join(sorted(missing_mapping))
        )

    # Normalize values for comparison without changing source files.
    for column in ["Item_Code", "Units"]:
        maintenance[column] = maintenance[column].astype("string").str.strip()

    for column in [
        "repair_type",
        "hsr_item_code",
        "required_unit",
        "description",
    ]:
        mapping[column] = mapping[column].astype("string").str.strip()

    maintenance["Item_Code_Normalized"] = (
        maintenance["Item_Code"].map(normalize_text)
    )
    maintenance["Unit_Normalized"] = (
        maintenance["Units"].map(normalize_text)
    )
    mapping["HSR_Code_Normalized"] = (
        mapping["hsr_item_code"].map(normalize_text)
    )
    mapping["Required_Unit_Normalized"] = (
        mapping["required_unit"].map(normalize_text)
    )

    # ---------------------------------------------------------
    # 1. Dataset overview
    # ---------------------------------------------------------
    print_section("1. HSR MAPPING AUDIT OVERVIEW")

    print(f"Maintenance records: {len(maintenance)}")
    print(
        "Distinct maintenance item codes: "
        f"{maintenance['Item_Code'].nunique(dropna=True)}"
    )
    print(
        "Distinct maintenance item-code/unit combinations: "
        f"{maintenance[['Item_Code', 'Units']].drop_duplicates().shape[0]}"
    )
    print(f"Configured HSR mappings: {len(mapping)}")

    print("\nMaintenance data status:")
    print(
        maintenance["Data_Status"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ---------------------------------------------------------
    # 2. Configured mapping table
    # ---------------------------------------------------------
    print_section("2. CONFIGURED HSR ACTIVITY MAPPINGS")

    if mapping.empty:
        print("WARNING: The mapping file contains no mappings.")
    else:
        print(
            mapping[
                [
                    "repair_type",
                    "hsr_item_code",
                    "required_unit",
                    "description",
                ]
            ].to_string(index=False)
        )

    # ---------------------------------------------------------
    # 3. Duplicate and incomplete mapping checks
    # ---------------------------------------------------------
    print_section("3. MAPPING CONFIGURATION VALIDATION")

    duplicate_codes = mapping[
        mapping["HSR_Code_Normalized"].duplicated(keep=False)
    ]

    print(
        "Mapping rows with repeated HSR codes: "
        f"{len(duplicate_codes)}"
    )

    if not duplicate_codes.empty:
        print(
            duplicate_codes[
                ["repair_type", "hsr_item_code", "required_unit"]
            ].to_string(index=False)
        )
        print(
            "NOTE: Repeated codes need review; they are not "
            "automatically assumed to be incorrect."
        )

    incomplete = mapping[
        mapping[
            [
                "repair_type",
                "hsr_item_code",
                "required_unit",
                "description",
            ]
        ].isna().any(axis=1)
        | (
            mapping[
                [
                    "repair_type",
                    "hsr_item_code",
                    "required_unit",
                    "description",
                ]
            ]
            .fillna("")
            .eq("")
            .any(axis=1)
        )
    ]

    print(f"Incomplete mapping rows: {len(incomplete)}")

    if not incomplete.empty:
        print(incomplete.to_string(index=False))

    duplicate_task_mappings = mapping[
        mapping["repair_type"].map(normalize_text).duplicated(
            keep=False
        )
    ]

    print(
        "Repair types appearing in multiple mapping rows: "
        f"{duplicate_task_mappings['repair_type'].nunique()}"
    )

    if not duplicate_task_mappings.empty:
        print(
            duplicate_task_mappings[
                ["repair_type", "hsr_item_code", "required_unit"]
            ].to_string(index=False)
        )
        print(
            "NOTE: Check these mappings manually to confirm that "
            "each repair type has the intended HSR activity."
        )

    # ---------------------------------------------------------
    # 4. Compare maintenance item codes and units with mappings
    # ---------------------------------------------------------
    print_section("4. MAINTENANCE ITEM MAPPING COVERAGE")

    mapping_lookup = mapping[
        [
            "HSR_Code_Normalized",
            "Required_Unit_Normalized",
            "repair_type",
            "hsr_item_code",
            "required_unit",
            "description",
        ]
    ].drop_duplicates()

    mapped_codes = set(
        mapping_lookup["HSR_Code_Normalized"].dropna()
    )

    maintenance["Mapping_Status"] = "NO_MAPPING"
    maintenance["Mapped_Repair_Type"] = pd.NA
    maintenance["Mapped_HSR_Code"] = pd.NA
    maintenance["Required_Unit"] = pd.NA

    for index, row in maintenance.iterrows():
        code = row["Item_Code_Normalized"]
        actual_unit = row["Unit_Normalized"]

        matches = mapping_lookup[
            mapping_lookup["HSR_Code_Normalized"] == code
        ]

        if matches.empty:
            continue

        # A matching item code alone is insufficient.
        compatible = matches[
            matches["Required_Unit_Normalized"] == actual_unit
        ]

        if compatible.empty:
            maintenance.at[index, "Mapping_Status"] = "UNIT_MISMATCH"
            maintenance.at[index, "Mapped_HSR_Code"] = "; ".join(
                matches["hsr_item_code"].dropna().astype(str).unique()
            )
            maintenance.at[index, "Required_Unit"] = "; ".join(
                matches["required_unit"].dropna().astype(str).unique()
            )
        elif len(compatible) == 1:
            selected = compatible.iloc[0]
            maintenance.at[index, "Mapping_Status"] = "CODE_UNIT_MATCH"
            maintenance.at[index, "Mapped_Repair_Type"] = (
                selected["repair_type"]
            )
            maintenance.at[index, "Mapped_HSR_Code"] = (
                selected["hsr_item_code"]
            )
            maintenance.at[index, "Required_Unit"] = (
                selected["required_unit"]
            )
        else:
            maintenance.at[index, "Mapping_Status"] = (
                "MULTIPLE_POSSIBLE_MAPPINGS"
            )

    print("\nMapping status by maintenance record:")
    print(
        maintenance["Mapping_Status"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nMaintenance items with no configured HSR code mapping:")

    unmapped = maintenance[
        maintenance["Mapping_Status"] == "NO_MAPPING"
    ]

    if unmapped.empty:
        print("None.")
    else:
        print(
            unmapped[
                ["Item_Code", "Units"]
            ]
            .drop_duplicates()
            .sort_values(["Item_Code", "Units"])
            .to_string(index=False)
        )

    print("\nMaintenance items with unit mismatches:")

    unit_mismatches = maintenance[
        maintenance["Mapping_Status"] == "UNIT_MISMATCH"
    ]

    if unit_mismatches.empty:
        print("None.")
    else:
        print(
            unit_mismatches[
                [
                    "Item_Code",
                    "Units",
                    "Mapped_HSR_Code",
                    "Required_Unit",
                ]
            ]
            .drop_duplicates()
            .to_string(index=False)
        )

    # ---------------------------------------------------------
    # 5. Summary by item code and unit
    # ---------------------------------------------------------
    print_section("5. MAPPING STATUS BY ITEM CODE AND UNIT")

    summary = (
        maintenance.groupby(
            ["Item_Code", "Units", "Mapping_Status"],
            dropna=False,
        )
        .agg(
            record_count=("RoadID_Raw", "size"),
            total_quantity=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values(
            ["Mapping_Status", "Item_Code", "Units"]
        )
    )

    print(summary.to_string(index=False))

    # ---------------------------------------------------------
    # 6. Optional comparison with extracted HSR norms
    # ---------------------------------------------------------
    print_section("6. EXTRACTED HSR RESOURCE NORMS")

    if HSR_NORMS_FILE.exists():
        norms = pd.read_csv(
            HSR_NORMS_FILE,
            dtype={"hsr_item_code": "string"},
        )

        print(f"Extracted HSR norm rows: {len(norms)}")
        print("Available norm columns:")
        print(", ".join(norms.columns.astype(str)))

        if "hsr_item_code" in norms.columns:
            norms["HSR_Code_Normalized"] = (
                norms["hsr_item_code"].map(normalize_text)
            )

            mapping_codes = set(
                mapping["HSR_Code_Normalized"].dropna()
            )
            norm_codes = set(
                norms["HSR_Code_Normalized"].dropna()
            )

            print(
                "Configured mapping codes found in norm file: "
                f"{len(mapping_codes & norm_codes)} of "
                f"{len(mapping_codes)}"
            )

            print(
                "Configured mapping codes missing from norm file: "
                f"{sorted(mapping_codes - norm_codes)}"
            )
        else:
            print(
                "WARNING: The norms file has no hsr_item_code column. "
                "Automatic code comparison was skipped."
            )
    else:
        print(
            "HSR norms file not found. The mapping audit can still "
            "continue, but norm-source verification was skipped."
        )

    # ---------------------------------------------------------
    # 7. Interpretation and limitations
    # ---------------------------------------------------------
    print_section("7. AUDIT LIMITATIONS")

    print(
        "- This script checks configured codes and unit labels; "
        "it does not prove that two activities are technically equivalent."
    )
    print(
        "- A code and unit match is only a preliminary mapping check."
    )
    print(
        "- Confirm activity descriptions, measurement basis, "
        "HSR source pages and notes before estimating resources."
    )
    print(
        "- Do not convert units or invent mappings to increase coverage."
    )
    print(
        "- Unmapped items should remain unmapped until supported "
        "by a verified source."
    )
    print(
        "- Budget quantities remain estimates, not actual resource "
        "consumption."
    )

    print_section("HSR MAPPING AUDIT COMPLETED")


if __name__ == "__main__":
    main()
