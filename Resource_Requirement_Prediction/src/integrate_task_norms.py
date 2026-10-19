
from pathlib import Path
import math

import pandas as pd

from estimate_resources import estimate_resources


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TASKS_FILE = PROJECT_ROOT / "data" / "demo" / "maintenance_tasks.csv"
MAPPING_FILE = (
    PROJECT_ROOT / "data" / "templates" / "hsr_activity_mapping.csv"
)
OUTPUT_FILE = PROJECT_ROOT / "outputs" / "task_resource_estimates.csv"


# --------------------------------------------------
# LOAD AND VALIDATE INPUT FILES
# --------------------------------------------------

def load_inputs():
    """Load task and HSR mapping files and validate their structure."""

    for file_path in [TASKS_FILE, MAPPING_FILE]:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required input file not found: {file_path}"
            )

    tasks = pd.read_csv(TASKS_FILE)
    mappings = pd.read_csv(MAPPING_FILE)

    required_task_columns = {
        "task_id",
        "repair_type",
        "quantity",
        "quantity_unit",
        "data_status",
    }

    required_mapping_columns = {
        "repair_type",
        "hsr_item_code",
        "required_unit",
        "description",
    }

    missing_tasks = required_task_columns - set(tasks.columns)
    missing_mappings = required_mapping_columns - set(mappings.columns)

    if missing_tasks:
        raise ValueError(
            "Maintenance tasks file is missing columns: "
            + ", ".join(sorted(missing_tasks))
        )

    if missing_mappings:
        raise ValueError(
            "HSR mapping file is missing columns: "
            + ", ".join(sorted(missing_mappings))
        )

    if tasks.empty:
        raise ValueError("The maintenance tasks file has no tasks.")

    if mappings.empty:
        raise ValueError("The HSR activity mapping file has no mappings.")

    for column in ["task_id", "repair_type", "quantity_unit"]:
        tasks[column] = tasks[column].fillna("").astype(str).str.strip()

    for column in ["repair_type", "hsr_item_code", "required_unit"]:
        mappings[column] = (
            mappings[column].fillna("").astype(str).str.strip()
        )

    if tasks["task_id"].eq("").any():
        raise ValueError("A maintenance task has a blank task ID.")

    if tasks["task_id"].duplicated().any():
        raise ValueError("Duplicate task IDs were found.")

    if tasks["repair_type"].eq("").any():
        raise ValueError("A maintenance task has a blank repair type.")

    if mappings[
        ["repair_type", "hsr_item_code", "required_unit"]
    ].eq("").any().any():
        raise ValueError("The HSR mapping contains blank required fields.")

    mappings["repair_type_key"] = (
        mappings["repair_type"].str.lower()
    )

    if mappings["repair_type_key"].duplicated().any():
        raise ValueError(
            "A repair type has multiple mappings. "
            "Resolve the mapping before estimating."
        )

    tasks["quantity_numeric"] = pd.to_numeric(
        tasks["quantity"], errors="coerce"
    )

    return tasks, mappings


# --------------------------------------------------
# ESTIMATE EACH MAINTENANCE TASK
# --------------------------------------------------

def process_tasks(tasks, mappings):
    """Match tasks to HSR norms and reject incompatible quantities."""

    mapping_lookup = {
        row["repair_type_key"]: row
        for _, row in mappings.iterrows()
    }

    results = []

    for _, task in tasks.iterrows():
        task_id = task["task_id"]
        repair_type = task["repair_type"]
        repair_type_key = repair_type.lower()
        task_status = str(task["data_status"]).strip().upper()
        quantity_unit = task["quantity_unit"].lower()
        quantity = task["quantity_numeric"]

        base_result = {
            "task_id": task_id,
            "repair_type": repair_type,
            "task_data_status": task_status,
            "task_quantity": quantity,
            "task_quantity_unit": quantity_unit,
        }

        # Do not accept blank or invalid quantities.
        if pd.isna(quantity) or not math.isfinite(float(quantity)):
            results.append({
                **base_result,
                "status": "INVALID_QUANTITY",
                "message": "Quantity must be a valid finite number.",
            })
            continue

        if quantity <= 0:
            results.append({
                **base_result,
                "status": "INVALID_QUANTITY",
                "message": "Quantity must be greater than zero.",
            })
            continue

        # SIMULATED tasks are only for software testing.
        if task_status not in {"ACTUAL", "ESTIMATE", "UNKNOWN", "SIMULATED"}:
            results.append({
                **base_result,
                "status": "INVALID_DATA_STATUS",
                "message": f"Unsupported data status: {task_status}",
            })
            continue

        # Find the matching HSR activity.
        mapping = mapping_lookup.get(repair_type_key)

        if mapping is None:
            results.append({
                **base_result,
                "status": "NO_MAPPING",
                "message": (
                    "No HSR mapping is available for this repair type."
                ),
            })
            continue

        hsr_code = mapping["hsr_item_code"]
        required_unit = mapping["required_unit"].lower()

        base_result["hsr_item_code"] = hsr_code
        base_result["required_unit"] = required_unit

        # Prevent interpreting a job count as metres, culverts, or volume.
        if quantity_unit != required_unit:
            results.append({
                **base_result,
                "status": "UNIT_MISMATCH",
                "message": (
                    f"Task unit is '{quantity_unit}', but HSR code "
                    f"{hsr_code} requires '{required_unit}'. "
                    "Enter a measured quantity in the required unit."
                ),
            })
            continue

        # Estimate resource requirements using the existing estimator.
        try:
            estimates = estimate_resources(hsr_code, quantity)

        except (ValueError, FileNotFoundError) as error:
            results.append({
                **base_result,
                "status": "ESTIMATION_ERROR",
                "message": str(error),
            })
            continue

        # One output row per resource required by the HSR norm.
        for _, estimate in estimates.iterrows():
            results.append({
                **base_result,
                "status": "ESTIMATED",
                "message": (
                    "HSR-based estimate. Verify assumptions and "
                    "local applicability before operational use."
                ),
                "resource_type": estimate["resource_type"],
                "resource_name": estimate["resource_name"],
                "estimated_resource_quantity":
                    estimate["estimated_resource_quantity"],
                "resource_unit": estimate["resource_unit"],
                "estimate_data_status": "ESTIMATE",
                "source_reference": estimate["source_reference"],
                "notes": estimate["notes"],
            })

    return pd.DataFrame(results)


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

def save_results(results):
    """Save the current run's results to a CSV file."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved current run results to:\n{OUTPUT_FILE}")
    print(f"Result rows: {len(results)}")


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():
    print("=" * 60)
    print("MAINTENANCE TASK TO HSR RESOURCE ESTIMATION")
    print("=" * 60)
    print("This program uses HSR norms to estimate resources.")
    print("It does not establish actual resource consumption.\n")

    try:
        tasks, mappings = load_inputs()
        results = process_tasks(tasks, mappings)

        display_columns = [
            column for column in [
                "task_id",
                "repair_type",
                "hsr_item_code",
                "status",
                "message",
                "resource_name",
                "estimated_resource_quantity",
                "resource_unit",
            ]
            if column in results.columns
        ]

        print(results[display_columns].to_string(index=False))

        save_results(results)

        print("\nStatus summary:")
        print(results["status"].value_counts().to_string())

        print(
            "\nReminder: SIMULATED demo tasks are for testing only. "
            "Do not use them as actual training data."
        )

    except (ValueError, FileNotFoundError, pd.errors.ParserError) as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()
