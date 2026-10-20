
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PREDICTION_FILE = ROOT / "outputs" / "predicted_task_requirements.csv"
AVAILABILITY_FILE = ROOT / "data" / "demo" / "resource_availability.csv"
OUTPUT_FILE = ROOT / "outputs" / "predicted_allocation_requirements.csv"

# Explicit demo-only assumptions.
# These mappings are not validated engineering rules.
RESOURCE_MAPPING = {
    "labour_person_days": ("skilled_worker", "person_days"),
    "asphalt_tonnes": ("asphalt_mix", "tonnes"),
    "aggregate_tonnes": ("aggregate", "tonnes"),
    "equipment_hours": ("roller", "machine_hours"),
}


def main():
    if not PREDICTION_FILE.is_file():
        raise FileNotFoundError(
            "Prediction file not found. Run "
            "python src/prediction_allocation_bridge.py first."
        )

    if not AVAILABILITY_FILE.is_file():
        raise FileNotFoundError(
            f"Availability file not found: {AVAILABILITY_FILE}"
        )

    predictions = pd.read_csv(PREDICTION_FILE)
    availability = pd.read_csv(AVAILABILITY_FILE)

    if len(predictions) != 1:
        raise ValueError(
            "This demo integration expects exactly one prediction row."
        )

    prediction = predictions.iloc[0]

    if prediction["data_status"] != "SIMULATED":
        raise ValueError(
            "This prototype only accepts explicitly simulated predictions."
        )

    if prediction["integration_status"] != (
        "PREDICTIONS_ONLY_NOT_ALLOCATED"
    ):
        raise ValueError("Unexpected prediction integration status.")

    required_columns = {
        "resource_name",
        "available_quantity",
        "unit",
    }
    if not required_columns.issubset(availability.columns):
        raise ValueError("Availability file is missing required columns.")

    rows = []

    for prediction_column, (resource_name, expected_unit) in (
        RESOURCE_MAPPING.items()
    ):
        quantity = float(prediction[prediction_column])

        if pd.isna(quantity) or quantity < 0:
            raise ValueError(
                f"Invalid predicted quantity: {prediction_column}"
            )

        matches = availability[
            availability["resource_name"] == resource_name
        ]

        if len(matches) != 1:
            raise ValueError(
                f"Expected exactly one availability row for {resource_name}."
            )

        available_unit = str(matches.iloc[0]["unit"])

        if available_unit != expected_unit:
            raise ValueError(
                f"Unit mismatch for {resource_name}: "
                f"expected {expected_unit}, found {available_unit}."
            )

        rows.append({
            "task_id": str(prediction["task_id"]),
            "resource_name": resource_name,
            "required_quantity": quantity,
            "unit": expected_unit,
            "data_status": "SIMULATED",
            "mapping_status": "DEMO_ASSUMPTION_NOT_VALIDATED",
        })

    result = pd.DataFrame(rows)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print("PREDICTION REQUIREMENTS CONVERSION")
    print("-" * 40)
    print(result.to_string(index=False))
    print(f"\nSaved: {OUTPUT_FILE}")
    print(
        "\nWARNING: These are demo-mapped requirements only. "
        "They have not been allocated by NSGA-II."
    )


if __name__ == "__main__":
    main()
