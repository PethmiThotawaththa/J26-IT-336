
from pathlib import Path

import pandas as pd
from joblib import load

MODEL_PATH = Path("outputs/demo_resource_model.joblib")

FEATURES = [
    "repair_type",
    "quantity",
    "quantity_unit",
    "priority",
]

TARGETS = [
    "labour_person_days",
    "asphalt_tonnes",
    "aggregate_tonnes",
    "equipment_hours",
]


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Saved model not found. Run src/train_resource_model.py first."
        )

    repair_type = input(
        "Repair type (pothole_patch/drain_cleaning/resurfacing): "
    ).strip().lower()

    quantity_unit = input("Quantity unit (sq_m/metres): ").strip().lower()

    try:
        quantity = float(input("Maintenance quantity: "))
        priority = float(input("Priority (0-10): "))
    except ValueError:
        raise ValueError("Quantity and priority must be numeric.")

    if not repair_type:
        raise ValueError("Repair type cannot be empty.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    if not 0 <= priority <= 10:
        raise ValueError("Priority must be between 0 and 10.")

    task = pd.DataFrame(
        [{
            "repair_type": repair_type,
            "quantity": quantity,
            "quantity_unit": quantity_unit,
            "priority": priority,
        }],
        columns=FEATURES,
    )

    model = load(MODEL_PATH)
    predictions = model.predict(task)[0]

    print("\n" + "=" * 48)
    print("RESOURCE REQUIREMENT PREDICTION")
    print("=" * 48)
    print("Repair type:", repair_type)
    print("Quantity:", quantity, quantity_unit)
    print("Priority:", priority)
    print("\nPredicted requirements (SIMULATED MODEL):")

    for name, value in zip(TARGETS, predictions):
        print(f"{name}: {value:.3f}")

    print(
        "\nWARNING: Prototype predictions only. "
        "Validate against approved norms or actual records "
        "before operational use."
    )


if __name__ == "__main__":
    main()
