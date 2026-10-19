
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "data" / "templates"

REQUIRED = {
    "maintenance_tasks.csv": {
        "task_id", "road_id", "repair_type", "priority",
        "source_id", "data_status"
    },
    "task_requirements.csv": {
        "task_id", "resource_type", "resource_name",
        "required_quantity", "unit", "data_status", "source_id"
    },
    "resource_availability.csv": {
        "resource_name", "available_quantity", "unit",
        "planning_period", "data_status", "source_id"
    },
    "source_register.csv": {
        "source_id", "source_name", "source_type",
        "source_status", "permission_status"
    },
}

ALLOWED_STATUS = {"ACTUAL", "ESTIMATE", "UNKNOWN"}
ALLOWED_RESOURCE_TYPES = {"LABOUR", "MATERIAL", "EQUIPMENT"}


def main():
    errors = []
    tables = {}

    # 1. Check that every template exists and is readable
    for filename, required_cols in REQUIRED.items():
        path = TEMPLATES / filename

        if not path.is_file():
            errors.append(f"{filename}: file does not exist")
            continue

        try:
            df = pd.read_csv(path)
        except (OSError, pd.errors.ParserError, UnicodeError) as exc:
            errors.append(f"{filename}: could not read CSV: {exc}")
            continue

        tables[filename] = df

        missing = required_cols - set(df.columns)
        if missing:
            errors.append(
                f"{filename}: missing columns {sorted(missing)}"
            )
            continue

        print(
            f"Checked {filename}: "
            f"{len(df)} data rows, {len(df.columns)} columns"
        )

        # 2. Validate status values
        if "data_status" in df.columns and not df.empty:
            values = set(
                df["data_status"]
                .dropna()
                .astype(str)
                .str.strip()
                .str.upper()
            )

            bad = values - ALLOWED_STATUS
            if bad:
                errors.append(
                    f"{filename}: unsupported data_status values "
                    f"{sorted(bad)}"
                )

            if df["data_status"].isna().any():
                errors.append(
                    f"{filename}: data_status contains empty values"
                )

        # 3. Validate non-negative numeric quantities
        for column in ("required_quantity", "available_quantity"):
            if column in df.columns and not df.empty:
                qty = pd.to_numeric(df[column], errors="coerce")

                if qty.isna().any():
                    errors.append(
                        f"{filename}: {column} must contain numeric values"
                    )
                elif (qty < 0).any():
                    errors.append(
                        f"{filename}: {column} must be non-negative"
                    )

        # 4. Check required identifiers are not blank
        for column in ("task_id", "road_id", "source_id"):
            if column in df.columns and not df.empty:
                blank = (
                    df[column].isna()
                    | df[column].astype(str).str.strip().eq("")
                )
                if blank.any():
                    errors.append(
                        f"{filename}: {column} contains blank values"
                    )

    # 5. Check duplicate task IDs
    tasks = tables.get("maintenance_tasks.csv")
    if tasks is not None and "task_id" in tasks.columns:
        if tasks["task_id"].dropna().duplicated().any():
            errors.append(
                "maintenance_tasks.csv: duplicate task_id values found"
            )

    # 6. Check resource types
    requirements = tables.get("task_requirements.csv")
    if requirements is not None and "resource_type" in requirements.columns:
        if not requirements.empty:
            values = set(
                requirements["resource_type"]
                .dropna()
                .astype(str)
                .str.strip()
                .str.upper()
            )
            bad = values - ALLOWED_RESOURCE_TYPES

            if bad:
                errors.append(
                    "task_requirements.csv: unsupported resource_type "
                    f"values {sorted(bad)}. Use LABOUR, MATERIAL, "
                    "or EQUIPMENT."
                )

    # 7. Check that requirements refer to known tasks
    if (
        tasks is not None
        and requirements is not None
        and "task_id" in tasks.columns
        and "task_id" in requirements.columns
        and not requirements.empty
    ):
        known_tasks = set(tasks["task_id"].dropna().astype(str).str.strip())
        referenced_tasks = set(
            requirements["task_id"].dropna().astype(str).str.strip()
        )
        unknown_tasks = referenced_tasks - known_tasks

        if unknown_tasks:
            errors.append(
                "task_requirements.csv: task_id values not found in "
                f"maintenance_tasks.csv: {sorted(unknown_tasks)}"
            )

    # 8. Check that referenced sources exist in the source register
    sources = tables.get("source_register.csv")
    if sources is not None and "source_id" in sources.columns:
        known_sources = set(
            sources["source_id"].dropna().astype(str).str.strip()
        )

        for filename in (
            "maintenance_tasks.csv",
            "task_requirements.csv",
            "resource_availability.csv",
        ):
            df = tables.get(filename)

            if (
                df is None
                or "source_id" not in df.columns
                or df.empty
            ):
                continue

            referenced_sources = set(
                df["source_id"].dropna().astype(str).str.strip()
            )
            unknown_sources = referenced_sources - known_sources

            if unknown_sources:
                errors.append(
                    f"{filename}: source_id values not found in "
                    f"source_register.csv: {sorted(unknown_sources)}"
                )

    # 9. Report results
    if errors:
        print("\nINPUT CHECK FAILED:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("\nInput structure and consistency checks passed.")
    print(
        "Empty templates are acceptable during setup. "
        "They do not establish data quality or model accuracy."
    )


if __name__ == "__main__":
    main()
