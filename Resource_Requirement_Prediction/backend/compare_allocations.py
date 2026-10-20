
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "data" / "demo"
OUTPUT_DIR = ROOT / "outputs"

TASKS_FILE = DEMO_DIR / "maintenance_tasks.csv"
REQUIREMENTS_FILE = DEMO_DIR / "task_requirements.csv"
AVAILABILITY_FILE = DEMO_DIR / "resource_availability.csv"

BASELINE_FILE = OUTPUT_DIR / "baseline_allocation.csv"
NSGA2_FILE = OUTPUT_DIR / "nsga2_allocation.csv"
REPORT_FILE = OUTPUT_DIR / "allocation_comparison.csv"


def load_inputs():
    """Load and validate simulated demonstration inputs."""
    tasks = pd.read_csv(TASKS_FILE)
    requirements = pd.read_csv(REQUIREMENTS_FILE)
    availability = pd.read_csv(AVAILABILITY_FILE)

    for name, frame in [
        ("tasks", tasks),
        ("requirements", requirements),
        ("availability", availability),
    ]:
        if "data_status" not in frame.columns:
            raise ValueError(f"{name} has no data_status column.")

        if not frame["data_status"].astype(str).str.upper().eq(
            "SIMULATED"
        ).all():
            raise ValueError(
                f"{name} contains non-simulated data. "
                "This script is for demonstration data only."
            )

    if tasks["task_id"].duplicated().any():
        raise ValueError("Tasks contain duplicate task_id values.")

    if requirements.duplicated(["task_id", "resource_name"]).any():
        raise ValueError(
            "Requirements contain duplicate task/resource rows."
        )

    if availability["resource_name"].duplicated().any():
        raise ValueError(
            "Availability contains duplicate resource_name values."
        )

    if not set(requirements["task_id"]).issubset(set(tasks["task_id"])):
        raise ValueError("Requirements reference unknown task IDs.")

    if not set(requirements["resource_name"]).issubset(
        set(availability["resource_name"])
    ):
        raise ValueError("Requirements reference unknown resources.")

    return tasks, requirements, availability


def prepare_allocation(frame, method):
    """Standardize allocation columns and validate quantities."""
    required_columns = {
        "task_id",
        "resource_name",
        "required_quantity",
        "allocated_quantity",
        "unit",
    }

    missing = required_columns - set(frame.columns)
    if missing:
        raise ValueError(
            f"{method} output is missing columns: {sorted(missing)}"
        )

    result = frame.copy()
    result["method"] = method

    for column in ["required_quantity", "allocated_quantity"]:
        result[column] = pd.to_numeric(
            result[column], errors="raise"
        )

    quantities = result[
        ["required_quantity", "allocated_quantity"]
    ].to_numpy(dtype=float)

    if not np.isfinite(quantities).all():
        raise ValueError(f"{method} contains non-finite quantities.")

    if (quantities < -1e-8).any():
        raise ValueError(f"{method} contains negative quantities.")

    if result.duplicated(["task_id", "resource_name"]).any():
        raise ValueError(
            f"{method} contains duplicate task/resource rows."
        )

    result["allocated_quantity"] = result[
        "allocated_quantity"
    ].clip(lower=0)

    result["shortage_quantity"] = (
        result["required_quantity"] - result["allocated_quantity"]
    ).clip(lower=0)

    return result


def calculate_metrics(frame, tasks):
    """Calculate shared shortage objectives and task completion."""
    task_priority = tasks.set_index("task_id")["priority"].to_dict()
    task_shortages = {}

    for task_id, group in frame.groupby("task_id"):
        positive = group[group["required_quantity"] > 0]

        if positive.empty:
            task_shortages[task_id] = 0.0
        else:
            proportions = (
                positive["shortage_quantity"]
                / positive["required_quantity"]
            )
            task_shortages[task_id] = float(proportions.mean())

    priorities = {
        task_id: float(task_priority[task_id])
        for task_id in task_shortages
    }

    priority_total = sum(priorities.values())

    if priority_total > 0:
        objective_1 = sum(
            priorities[task_id] / priority_total
            * task_shortages[task_id]
            for task_id in task_shortages
        )
    else:
        objective_1 = float(np.mean(list(task_shortages.values())))

    objective_2 = max(task_shortages.values(), default=0.0)

    task_complete = {}

    for task_id, group in frame.groupby("task_id"):
        positive = group[group["required_quantity"] > 0]

        task_complete[task_id] = bool(
            (
                positive["allocated_quantity"]
                >= positive["required_quantity"] - 1e-8
            ).all()
        )

    return {
        "Objective_1_Weighted_Shortage": objective_1,
        "Objective_2_Worst_Task_Shortage": objective_2,
        "Fully_Completed_Tasks": sum(task_complete.values()),
        "Total_Tasks": len(task_complete),
    }


def check_resource_capacity(frame, availability):
    """Check total allocated quantity against resource capacity."""
    supply = availability.set_index(
        "resource_name"
    )["available_quantity"].to_dict()

    resource_units = availability.set_index(
        "resource_name"
    )["unit"].to_dict()

    problems = []

    for resource_name, group in frame.groupby("resource_name"):
        if resource_name not in supply:
            problems.append(f"{resource_name}: missing supply record")
            continue

        expected_unit = str(resource_units[resource_name]).strip()
        actual_units = group["unit"].astype(str).str.strip()

        if not actual_units.eq(expected_unit).all():
            problems.append(f"{resource_name}: unit mismatch")
            continue

        total_allocated = float(group["allocated_quantity"].sum())
        available = float(supply[resource_name])

        if total_allocated > available + 1e-6:
            problems.append(
                f"{resource_name}: allocated {total_allocated:.4f}, "
                f"available {available:.4f}"
            )

    return problems


def main():
    tasks, requirements, availability = load_inputs()

    if not BASELINE_FILE.exists():
        raise FileNotFoundError(
            "Baseline output not found. Run: "
            "python backend\\allocate_baseline.py"
        )

    if not NSGA2_FILE.exists():
        raise FileNotFoundError(
            "NSGA-II output not found. Run: "
            "python backend\\optimize_allocation.py"
        )

    baseline_raw = pd.read_csv(BASELINE_FILE)
    nsga2_raw = pd.read_csv(NSGA2_FILE)

    baseline = prepare_allocation(
        baseline_raw, "Greedy baseline"
    )
    nsga2 = prepare_allocation(
        nsga2_raw, "NSGA-II"
    )

    expected = requirements[
        ["task_id", "resource_name", "required_quantity", "unit"]
    ].copy()

    expected_keys = set(
        zip(expected["task_id"], expected["resource_name"])
    )

    for method, result in [
        ("Greedy baseline", baseline),
        ("NSGA-II", nsga2),
    ]:
        actual_keys = set(
            zip(result["task_id"], result["resource_name"])
        )

        if actual_keys != expected_keys:
            raise ValueError(
                f"{method} output does not match the expected "
                "task/resource rows."
            )

        checked = result.merge(
            expected,
            on=["task_id", "resource_name"],
            suffixes=("_output", "_input"),
            validate="one_to_one",
        )

        if not np.allclose(
            checked["required_quantity_output"].to_numpy(dtype=float),
            checked["required_quantity_input"].to_numpy(dtype=float),
        ):
            raise ValueError(
                f"{method} demand quantities do not match the inputs."
            )

        output_units = (
            checked["unit_output"].astype(str).str.strip().to_numpy()
        )
        input_units = (
            checked["unit_input"].astype(str).str.strip().to_numpy()
        )

        if not np.array_equal(output_units, input_units):
            raise ValueError(
                f"{method} units do not match the input requirements."
            )

    report_rows = []

    for method, result in [
        ("Greedy baseline", baseline),
        ("NSGA-II", nsga2),
    ]:
        metrics = calculate_metrics(result, tasks)
        capacity_problems = check_resource_capacity(
            result, availability
        )

        metrics["Method"] = method
        metrics["Capacity_Valid"] = not capacity_problems
        metrics["Capacity_Issues"] = "; ".join(capacity_problems)

        report_rows.append(metrics)

    report = pd.DataFrame(report_rows)

    column_order = [
        "Method",
        "Objective_1_Weighted_Shortage",
        "Objective_2_Worst_Task_Shortage",
        "Fully_Completed_Tasks",
        "Total_Tasks",
        "Capacity_Valid",
        "Capacity_Issues",
    ]

    report = report[column_order]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report.to_csv(REPORT_FILE, index=False)

    print("\nFAIR ALLOCATION COMPARISON")
    print(report.to_string(index=False))

    print("\nInterpretation:")
    print("- Lower Objective 1 is better.")
    print("- Lower Objective 2 is better.")
    print("- More fully completed tasks is better.")
    print("- Capacity_Valid must be True for a feasible result.")
    print(
        "\nThese metrics describe simulated demonstration data only."
    )
    print(f"Saved comparison: {REPORT_FILE}")


if __name__ == "__main__":
    main()
