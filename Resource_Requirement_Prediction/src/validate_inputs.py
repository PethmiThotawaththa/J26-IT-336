from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "data/templates"
REQUIRED = {
    "maintenance_tasks.csv": {
        "task_id", "road_id", "repair_type", "priority", "source_id", "data_status"
    },
    "task_requirements.csv": {
        "task_id", "resource_type", "resource_name", "required_quantity",
        "unit", "data_status", "source_id"
    },
    "resource_availability.csv": {
        "resource_name", "available_quantity", "unit", "planning_period",
        "data_status", "source_id"
    },
    "source_register.csv": {
        "source_id", "source_name", "source_type", "source_status", "permission_status"
    },
}
ALLOWED_STATUS = {"ACTUAL", "ESTIMATE", "UNKNOWN"}

def main():
    errors = []
    for filename, required_cols in REQUIRED.items():
        path = TEMPLATES / filename
        df = pd.read_csv(path)
        missing = required_cols - set(df.columns)
        if missing:
            errors.append(f"{filename}: missing columns {sorted(missing)}")
        if "data_status" in df.columns and not df.empty:
            values = set(df["data_status"].dropna().astype(str).str.upper())
            bad = values - ALLOWED_STATUS
            if bad:
                errors.append(
                    f"{filename}: unsupported data_status values {sorted(bad)}. "
                    "Use ACTUAL, ESTIMATE, or UNKNOWN in research templates."
                )
        if "required_quantity" in df.columns and not df.empty:
            qty = pd.to_numeric(df["required_quantity"], errors="coerce")
            if qty.isna().any() or (qty < 0).any():
                errors.append(f"{filename}: required_quantity must be numeric and non-negative")
        if "available_quantity" in df.columns and not df.empty:
            qty = pd.to_numeric(df["available_quantity"], errors="coerce")
            if qty.isna().any() or (qty < 0).any():
                errors.append(f"{filename}: available_quantity must be numeric and non-negative")

    if errors:
        print("INPUT CHECK FAILED:")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    print("Template structure checks passed.")
    print("Empty templates are expected at the beginning; this does NOT validate research data quality.")

if __name__ == "__main__":
    main()
