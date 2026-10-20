
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"

PARETO_FILE = OUTPUT_DIR / "predicted_nsga2_pareto_solutions.csv"
TASKS_FILE = (
    OUTPUT_DIR
    / "prediction_allocation_test_inputs"
    / "maintenance_tasks.csv"
)
REQUIREMENTS_FILE = (
    OUTPUT_DIR
    / "prediction_allocation_test_inputs"
    / "task_requirements.csv"
)
AVAILABILITY_FILE = (
    ROOT / "data" / "demo" / "resource_availability.csv"
)

PREDICTED_TASK_ID = "PREDICTED-DEMO-01"
RESULT_FILE = OUTPUT_DIR / "compromise_strategy_comparison.csv"


def main():
    # Check the input files.
    for path in [
        PARETO_FILE,
        TASKS_FILE,
        REQUIREMENTS_FILE,
        AVAILABILITY_FILE,
    ]:
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

    pareto = pd.read_csv(PARETO_FILE)
    tasks = pd.read_csv(TASKS_FILE)
    requirements = pd.read_csv(REQUIREMENTS_FILE)
    availability = pd.read_csv(AVAILABILITY_FILE)

    if pareto.empty:
        raise ValueError("The Pareto solutions file is empty.")

    required_objectives = [
        "objective_1_weighted_shortage",
        "objective_2_worst_task_shortage",
    ]
    if not set(required_objectives).issubset(pareto.columns):
        raise ValueError("Required objective columns are missing.")

    if "allocation_fractions" not in pareto.columns:
        raise ValueError("Allocation fractions are missing.")

    # Match the optimizer's requirement ordering.
    task_ids = requirements["task_id"].astype(str).to_numpy()
    resource_names = requirements["resource_name"].astype(str).to_numpy()
    demands = pd.to_numeric(
        requirements["required_quantity"], errors="raise"
    ).to_numpy(dtype=float)

    supply = availability.set_index(
        "resource_name"
    )["available_quantity"].astype(float).to_dict()

    if (demands < 0).any():
        raise ValueError("Negative requirements found.")

    if not set(resource_names).issubset(set(supply)):
        raise ValueError("A required resource is missing from availability.")

    predicted_mask = task_ids == PREDICTED_TASK_ID
    if not predicted_mask.any():
        raise ValueError("Predicted task not found in requirements.")

    task_priorities = tasks.set_index(
        tasks["task_id"].astype(str)
    )["priority"].astype(float).to_dict()

    # Reproduce the optimizer's allocation decoding:
    # allocation fractions are clipped to [0, 1], then each resource's
    # total is scaled down if it exceeds the available capacity.
    def decode(fractions):
        allocated = np.clip(
            np.asarray(fractions, dtype=float), 0.0, 1.0
        ) * demands

        for resource_name, available_quantity in supply.items():
            indices = np.where(resource_names == resource_name)[0]
            total = allocated[indices].sum()

            if total > available_quantity and total > 0:
                allocated[indices] *= available_quantity / total

        return allocated

    # Recalculate both objectives using the optimizer's objective logic.
    def calculate_objectives(allocated):
        positive = demands > 0
        shortages = np.zeros(len(demands))
        shortages[positive] = (
            demands[positive] - allocated[positive]
        ) / demands[positive]

        task_shortages = {}
        for task_id in tasks["task_id"].astype(str):
            indices = np.where(
                (task_ids == task_id) & positive
            )[0]
            task_shortages[task_id] = (
                float(shortages[indices].mean())
                if len(indices) else 0.0
            )

        priority_total = sum(task_priorities.values())
        if priority_total > 0:
            objective_1 = sum(
                task_priorities[task_id] / priority_total
                * task_shortages[task_id]
                for task_id in task_shortages
            )
        else:
            objective_1 = float(np.mean(list(task_shortages.values())))

        objective_2 = max(task_shortages.values(), default=0.0)
        return objective_1, objective_2, task_shortages

    candidates = []

    for row_index, row in pareto.iterrows():
        try:
            fractions = [
                float(value)
                for value in str(row["allocation_fractions"]).split(";")
            ]
        except ValueError as exc:
            raise ValueError(
                f"Invalid allocation fractions in Pareto row {row_index}."
            ) from exc

        if len(fractions) != len(demands):
            raise ValueError(
                f"Pareto row {row_index} has {len(fractions)} fractions, "
                f"but {len(demands)} requirements exist. "
                "The saved candidates and test inputs may not match."
            )

        allocated = decode(fractions)
        objective_1, objective_2, task_shortages = (
            calculate_objectives(allocated)
        )

        predicted_indices = np.where(predicted_mask)[0]
        predicted_required = demands[predicted_indices].sum()
        predicted_shortage = (
            (demands[predicted_indices] - allocated[predicted_indices])
            / np.where(demands[predicted_indices] > 0,
                       demands[predicted_indices], 1.0)
        )

        predicted_average_shortage = float(
            predicted_shortage.mean()
        )

        # Calculate normalized distance to the ideal point.
        candidates.append({
            "solution_id": row.get("solution_id", row_index + 1),
            "allocation": allocated,
            "objective_1": objective_1,
            "objective_2": objective_2,
            "predicted_task_shortage": predicted_average_shortage,
            "predicted_task_required_total": predicted_required,
            "predicted_task_allocated_total": float(
                allocated[predicted_indices].sum()
            ),
            "task_shortages": task_shortages,
        })

    # Use recalculated objective values for all strategies.
    objective_values = np.array([
        [candidate["objective_1"], candidate["objective_2"]]
        for candidate in candidates
    ])
    minimum = objective_values.min(axis=0)
    maximum = objective_values.max(axis=0)
    ranges = maximum - minimum

    normalized = np.zeros_like(objective_values)
    for column in range(2):
        if ranges[column] > 1e-12:
            normalized[:, column] = (
                objective_values[:, column] - minimum[column]
            ) / ranges[column]

    for index, candidate in enumerate(candidates):
        candidate["normalized_distance"] = float(
            np.sqrt(np.sum(normalized[index] ** 2))
        )

    # Strategy 1: the current normalized-distance compromise.
    current = min(
        candidates,
        key=lambda item: item["normalized_distance"]
    )

    # Strategy 2: minimize the weighted-shortage objective.
    weighted = min(
        candidates,
        key=lambda item: (
            item["objective_1"],
            item["objective_2"]
        )
    )

    # Strategy 3: minimize worst-task shortage first.
    balanced = min(
        candidates,
        key=lambda item: (
            item["objective_2"],
            item["objective_1"]
        )
    )

    strategies = [
        ("Current normalized compromise", current),
        ("Weighted-shortage first", weighted),
        ("Worst-task shortage first", balanced),
    ]

    result_rows = []

    for strategy_name, candidate in strategies:
        allocated = candidate["allocation"]

        for index, requirement in requirements.iterrows():
            required = float(requirement["required_quantity"])
            allocation_quantity = float(allocated[index])

            result_rows.append({
                "strategy": strategy_name,
                "solution_id": candidate["solution_id"],
                "task_id": str(requirement["task_id"]),
                "resource_name": str(requirement["resource_name"]),
                "required_quantity": required,
                "allocated_quantity": allocation_quantity,
                "shortage_quantity": max(
                    0.0, required - allocation_quantity
                ),
                "unit": str(requirement["unit"]),
                "objective_1_weighted_shortage":
                    candidate["objective_1"],
                "objective_2_worst_task_shortage":
                    candidate["objective_2"],
                "predicted_task_average_shortage":
                    candidate["predicted_task_shortage"],
                "data_status": "SIMULATED",
            })

    result = pd.DataFrame(result_rows)
    result.to_csv(RESULT_FILE, index=False)

    print("ALLOCATION STRATEGY COMPARISON")
    print("=" * 45)

    summary_rows = []
    for strategy_name, candidate in strategies:
        predicted_indices = np.where(predicted_mask)[0]
        allocated = candidate["allocation"]

        summary_rows.append({
            "strategy": strategy_name,
            "solution_id": candidate["solution_id"],
            "objective_1": round(candidate["objective_1"], 6),
            "objective_2": round(candidate["objective_2"], 6),
            "predicted_task_average_shortage": round(
                candidate["predicted_task_shortage"], 6
            ),
            "predicted_task_allocated_resources": round(
                float(allocated[predicted_indices].sum()), 6
            ),
            "data_status": "SIMULATED",
        })

    summary = pd.DataFrame(summary_rows)
    print(summary.to_string(index=False))

    # Independently verify capacities for every selected strategy.
    print("\nCAPACITY CHECKS")
    for strategy_name, candidate in strategies:
        allocated = candidate["allocation"]
        valid = True

        for resource_name, available_quantity in supply.items():
            indices = np.where(resource_names == resource_name)[0]
            total = float(allocated[indices].sum())

            if total > available_quantity + 1e-6:
                valid = False
                print(
                    f"{strategy_name}: capacity violation for "
                    f"{resource_name}"
                )

        print(f"{strategy_name}: {'PASSED' if valid else 'FAILED'}")

        if not valid:
            raise RuntimeError(
                f"Capacity validation failed for {strategy_name}."
            )

    print(f"\nDetailed comparison saved: {RESULT_FILE}")
    print(
        "WARNING: Results use simulated inputs and unvalidated "
        "labour/equipment mappings."
    )


if __name__ == "__main__":
    main()
