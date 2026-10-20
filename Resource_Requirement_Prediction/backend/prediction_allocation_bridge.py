
from pathlib import Path

import pandas as pd
from joblib import load

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "outputs" / "demo_resource_model.joblib"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "predicted_task_requirements.csv"

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

ALLOWED_UNITS = {
    "pothole_patch": "sq_m",
    "drain_cleaning": "metres",
    "resurfacing": "sq_m",
}


def main():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            "Trained model not found. Run "
            "python src/train_resource_model.py first."
        )

    print("PREDICTION-TO-ALLOCATION BRIDGE")
    print("SIMULATED RESEARCH PROTOTYPE")
    print("-" * 40)

    repair_type = input(
        "Repair type (pothole_patch/drain_cleaning/resurfacing): "
    ).strip().lower()

    if repair_type not in ALLOWED_UNITS:
        raise ValueError("Unsupported repair type.")

    quantity_unit = input(
        f"Quantity unit ({ALLOWED_UNITS[repair_type]}): "
    ).strip().lower()

    if quantity_unit != ALLOWED_UNITS[repair_type]:
        raise ValueError(
            f"{repair_type} requires the unit "
            f"{ALLOWED_UNITS[repair_type]} in this demo."
        )

    try:
        quantity = float(input("Maintenance quantity: "))
        priority = float(input("Priority (0-10): "))
    except ValueError as exc:
        raise ValueError(
            "Quantity and priority must be numeric."
        ) from exc

    if not 0 < quantity <= 1_000_000:
        raise ValueError(
            "Quantity must be greater than 0 and at most 1,000,000."
        )

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
    values = model.predict(task)[0]

    predictions = {
        name: float(value)
        for name, value in zip(TARGETS, values)
    }

    for name, value in predictions.items():
        if (
            not pd.notna(value)
            or value == float("inf")
            or value == float("-inf")
        ):
            raise ValueError(f"Invalid model output for {name}.")

        if value < 0:
            raise ValueError(
                f"Model returned a negative requirement for {name}."
            )

    result = {
        "task_id": "PREDICTED-DEMO-01",
        **task.iloc[0].to_dict(),
        **predictions,
        "data_status": "SIMULATED",
        "integration_status": "PREDICTIONS_ONLY_NOT_ALLOCATED",
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result]).to_csv(OUTPUT_FILE, index=False)

    print("\nPredicted requirements:")
    for name, value in predictions.items():
        print(f"{name}: {value:.3f}")

    print("\nSaved predictions:", OUTPUT_FILE)
    print("Data status: SIMULATED")
    print(
        "These predictions have not been mapped to specific "
        "worker or equipment categories and have not been "
        "passed to NSGA-II."
    )


if __name__ == "__main__":
    main()
