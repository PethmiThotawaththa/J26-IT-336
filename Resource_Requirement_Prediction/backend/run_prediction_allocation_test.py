
from pathlib import Path
import sys
import pandas as pd

# Allow Python to import the existing optimizer from src.
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

sys.path.insert(0, str(SRC_DIR))
import optimize_allocation as optimizer


# Input files
OUTPUT_DIR = ROOT / "outputs"

PREDICTION_DETAILS_FILE = (
    OUTPUT_DIR / "predicted_task_requirements.csv"
)

PREDICTION_REQUIREMENTS_FILE = (
    OUTPUT_DIR / "predicted_allocation_requirements.csv"
)

ORIGINAL_TASKS_FILE = ROOT / "data" / "demo" / "maintenance_tasks.csv"
ORIGINAL_REQUIREMENTS_FILE = (
    ROOT / "data" / "demo" / "task_requirements.csv"
)
ORIGINAL_AVAILABILITY_FILE = (
    ROOT / "data" / "demo" / "resource_availability.csv"
)

# Separate test input and output files.
TEST_DIR = OUTPUT_DIR / "prediction_allocation_test_inputs"
TEST_TASKS_FILE = TEST_DIR / "maintenance_tasks.csv"
TEST_REQUIREMENTS_FILE = TEST_DIR / "task_requirements.csv"

TEST_ALLOCATION_FILE = (
    OUTPUT_DIR / "predicted_nsga2_allocation.csv"
)
TEST_PARETO_FILE = (
    OUTPUT_DIR / "predicted_nsga2_pareto_solutions.csv"
)


def main():
    print("PREDICTION + NSGA-II INTEGRATION TEST")
    print("=" * 45)

    # 1. Check required files.
    required_files = [
        PREDICTION_DETAILS_FILE,
        PREDICTION_REQUIREMENTS_FILE,
        ORIGINAL_TASKS_FILE,
        ORIGINAL_REQUIREMENTS_FILE,
        ORIGINAL_AVAILABILITY_FILE,
    ]

    for file_path in required_files:
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Required file not found: {file_path}"
            )

    # 2. Read existing demo data without modifying the originals.
    tasks = pd.read_csv(ORIGINAL_TASKS_FILE)
    requirements = pd.read_csv(ORIGINAL_REQUIREMENTS_FILE)
    availability = pd.read_csv(ORIGINAL_AVAILABILITY_FILE)

    # Prediction details contain repair type, quantity, unit and priority.
    prediction_details = pd.read_csv(PREDICTION_DETAILS_FILE)

    # Converted requirements contain resource names and required quantities.
    predicted_requirements = pd.read_csv(
        PREDICTION_REQUIREMENTS_FILE
    )

    if len(prediction_details) != 1:
        raise ValueError(
            "Expected exactly one prediction details row."
        )

    if len(predicted_requirements) != 4:
        raise ValueError(
            "Expected exactly four predicted resource requirements."
        )

    detail = prediction_details.iloc[0]

    task_id = str(detail["task_id"])

    # 3. Validate the prediction and its conversion.
    if str(detail["data_status"]) != "SIMULATED":
        raise ValueError(
            "The prediction must be marked SIMULATED."
        )

    if str(detail["integration_status"]) != (
        "PREDICTIONS_ONLY_NOT_ALLOCATED"
    ):
        raise ValueError(
            "Unexpected prediction integration status."
        )

    if not (
        predicted_requirements["data_status"] == "SIMULATED"
    ).all():
        raise ValueError(
            "All converted requirements must be SIMULATED."
        )

    if not (
        predicted_requirements["mapping_status"]
        == "DEMO_ASSUMPTION_NOT_VALIDATED"
    ).all():
        raise ValueError(
            "Unexpected resource mapping status."
        )

    if not (
        predicted_requirements["task_id"].astype(str) == task_id
    ).all():
        raise ValueError(
            "Prediction details and converted requirements "
            "refer to different tasks."
        )

    if task_id in tasks["task_id"].astype(str).tolist():
        raise ValueError(
            f"Task ID {task_id} already exists in the demo tasks."
        )

    # 4. Confirm that every predicted resource exists in availability.
    if availability["resource_name"].duplicated().any():
        raise ValueError(
            "Availability contains duplicate resource names."
        )

    for _, row in predicted_requirements.iterrows():
        resource_name = str(row["resource_name"])
        expected_unit = str(row["unit"])

        matches = availability[
            availability["resource_name"] == resource_name
        ]

        if len(matches) != 1:
            raise ValueError(
                f"Resource '{resource_name}' must appear exactly "
                "once in the availability file."
            )

        available_unit = str(matches.iloc[0]["unit"])

        if available_unit != expected_unit:
            raise ValueError(
                f"Unit mismatch for {resource_name}: "
                f"requirement unit is {expected_unit}, "
                f"availability unit is {available_unit}."
            )

    # 5. Create a task row using the existing task columns.
    task = {column: "" for column in tasks.columns}

    task_values = {
        "task_id": task_id,
        "road_id": "DEMO-PREDICTED-ROAD",
        "road_section": "DEMO-SECTION",
        "repair_type": str(detail["repair_type"]),
        "priority": float(detail["priority"]),
        "quantity": float(detail["quantity"]),
        "quantity_unit": str(detail["quantity_unit"]),
        "source_id": "PREDICTION-BRIDGE-DEMO",
        "data_status": "SIMULATED",
        "notes": (
            "Predicted task for integration testing. "
            "Labour and equipment resource mappings are "
            "unvalidated demo assumptions."
        ),
    }

    for column, value in task_values.items():
        if column in task:
            task[column] = value

    tasks = pd.concat(
        [
            tasks,
            pd.DataFrame([task], columns=tasks.columns),
        ],
        ignore_index=True,
    )

    # 6. Convert predicted requirements to the optimizer's schema.
    required_requirement_columns = set(requirements.columns)

    missing_columns = (
        required_requirement_columns
        - set(predicted_requirements.columns)
    )

    # The converted file may not include source_id or notes.
    # Add these fields explicitly for the optimizer's input format.
    new_requirements = predicted_requirements[
        ["task_id", "resource_name", "required_quantity", "unit"]
    ].copy()

    new_requirements["data_status"] = "SIMULATED"

    if "source_id" in requirements.columns:
        new_requirements["source_id"] = "PREDICTION-BRIDGE-DEMO"

    if "notes" in requirements.columns:
        new_requirements["notes"] = (
            "Unvalidated demo mapping; not an engineering recommendation."
        )

    # Keep the exact column order expected by the existing optimizer.
    new_requirements = new_requirements.reindex(
        columns=requirements.columns
    )

    requirements = pd.concat(
        [requirements, new_requirements],
        ignore_index=True,
    )

    # 7. Validate task references and resource names.
    task_ids = set(tasks["task_id"].astype(str))
    requirement_task_ids = set(
        requirements["task_id"].astype(str)
    )

    if not requirement_task_ids.issubset(task_ids):
        raise ValueError(
            "Some requirements reference tasks that do not exist."
        )

    availability_names = set(
        availability["resource_name"].astype(str)
    )

    requirement_names = set(
        requirements["resource_name"].astype(str)
    )

    if not requirement_names.issubset(availability_names):
        raise ValueError(
            "Some requirements reference unavailable resource names."
        )

    if requirements.duplicated(
        ["task_id", "resource_name"]
    ).any():
        raise ValueError(
            "Duplicate task/resource requirement pairs detected."
        )

    # 8. Save isolated test inputs.
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tasks.to_csv(TEST_TASKS_FILE, index=False)
    requirements.to_csv(TEST_REQUIREMENTS_FILE, index=False)

    # 9. Redirect the optimizer to the isolated test files.
    # The original demo inputs and outputs are not overwritten.
    optimizer.TASKS_FILE = TEST_TASKS_FILE
    optimizer.REQUIREMENTS_FILE = TEST_REQUIREMENTS_FILE
    optimizer.AVAILABILITY_FILE = ORIGINAL_AVAILABILITY_FILE
    optimizer.OUTPUT_FILE = TEST_ALLOCATION_FILE
    optimizer.PARETO_FILE = TEST_PARETO_FILE

    print(f"Original demo tasks: {len(tasks) - 1}")
    print(f"Predicted tasks added: 1")
    print(f"Total tasks for test: {len(tasks)}")
    print(f"Total requirements: {len(requirements)}")
    print(f"Predicted task ID: {task_id}")
    print("\nTest input files saved:")
    print(TEST_TASKS_FILE)
    print(TEST_REQUIREMENTS_FILE)

    print("\nStarting NSGA-II using isolated test files...")
    print("-" * 45)

    # 10. Run the existing optimizer.
    optimizer.main()

    # 11. Verify the generated allocation.
    if not TEST_ALLOCATION_FILE.is_file():
        raise FileNotFoundError(
            "The optimizer did not create the test allocation file."
        )

    allocation = pd.read_csv(TEST_ALLOCATION_FILE)

    predicted_allocation = allocation[
        allocation["task_id"].astype(str) == task_id
    ]

    if predicted_allocation.empty:
        raise RuntimeError(
            "The predicted task was not found in the allocation output."
        )

    if not TEST_PARETO_FILE.is_file():
        raise FileNotFoundError(
            "The optimizer did not create the test Pareto file."
        )

    print("\nINTEGRATION OUTPUT CHECK")
    print("-" * 45)

    display_columns = [
        column
        for column in [
            "task_id",
            "resource_name",
            "required_quantity",
            "allocated_quantity",
            "shortage_quantity",
            "unit",
            "allocation_status",
            "data_status",
        ]
        if column in predicted_allocation.columns
    ]

    print(
        predicted_allocation[display_columns].to_string(index=False)
    )

    # Independently check aggregate resource capacity.
    allocation_totals = allocation.groupby(
        "resource_name"
    )["allocated_quantity"].sum()

    availability_totals = availability.set_index(
        "resource_name"
    )["available_quantity"]

    capacity_valid = True

    for resource_name, allocated_quantity in allocation_totals.items():
        available_quantity = float(
            availability_totals[resource_name]
        )

        if float(allocated_quantity) > available_quantity + 1e-6:
            capacity_valid = False
            print(
                f"CAPACITY ERROR: {resource_name}: "
                f"allocated={allocated_quantity}, "
                f"available={available_quantity}"
            )

    if not capacity_valid:
        raise RuntimeError(
            "Independent capacity validation failed."
        )

    print("\nIndependent capacity validation: PASSED")
    print(f"Test allocation: {TEST_ALLOCATION_FILE}")
    print(f"Test Pareto set: {TEST_PARETO_FILE}")
    print(
        "\nWARNING: This is a simulated research prototype. "
        "The labour and equipment mappings are unvalidated "
        "assumptions, not verified engineering recommendations."
    )


if __name__ == "__main__":
    main()
