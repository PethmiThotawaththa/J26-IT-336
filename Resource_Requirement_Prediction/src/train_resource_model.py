
from pathlib import Path
import json

import pandas as pd
import sklearn
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA_PATH = Path("data/demo/ml_training_data.csv")
OUTPUT_DIR = Path("outputs")
MODEL_PATH = OUTPUT_DIR / "demo_resource_model.joblib"
METRICS_PATH = OUTPUT_DIR / "demo_model_metadata.json"

FEATURES = ["repair_type", "quantity", "quantity_unit", "priority"]
TARGETS = [
    "labour_person_days",
    "asphalt_tonnes",
    "aggregate_tonnes",
    "equipment_hours",
]


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = FEATURES + TARGETS + ["data_status"]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Prevent simulated examples from being mistaken for real training data.
    statuses = set(df["data_status"].dropna().astype(str).str.upper())
    if statuses != {"SIMULATED"}:
        raise ValueError(
            "This demo training script accepts SIMULATED records only. "
            "Create a separately reviewed workflow for real or estimated data."
        )

    if df[required].isna().any().any():
        raise ValueError("Required columns contain missing values.")

    if len(df) < 12:
        raise ValueError("At least 12 records are required for this demo split.")

    for column in ["quantity", "priority"] + TARGETS:
        df[column] = pd.to_numeric(df[column], errors="raise")
        if not df[column].map(lambda value: pd.notna(value) and value >= 0).all():
            raise ValueError(f"{column} must contain non-negative numbers.")

    if not df["repair_type"].nunique() >= 2:
        raise ValueError("At least two repair types are needed for this demo.")

    X = df[FEATURES]
    y = df[TARGETS]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=df["repair_type"],
    )

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                ["repair_type", "quantity_unit"],
            ),
            ("numeric", "passthrough", ["quantity", "priority"]),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=200,
                    random_state=42,
                    min_samples_leaf=1,
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    per_target_metrics = {}
    for index, target in enumerate(TARGETS):
        actual = y_test[target].to_numpy()
        predicted = predictions[:, index]
        per_target_metrics[target] = {
            "mae": float(mean_absolute_error(actual, predicted)),
            "rmse": float(mean_squared_error(actual, predicted) ** 0.5),
        }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dump(model, MODEL_PATH)

    metadata = {
        "model_type": "RandomForestRegressor",
        "purpose": "SIMULATED_PIPELINE_TEST_ONLY",
        "training_data_status": "SIMULATED",
        "dataset": str(DATA_PATH),
        "records_total": int(len(df)),
        "records_train": int(len(X_train)),
        "records_test": int(len(X_test)),
        "features": FEATURES,
        "targets": TARGETS,
        "metrics": per_target_metrics,
        "random_state": 42,
        "scikit_learn_version": sklearn.__version__,
        "warning": (
            "Metrics use invented simulated examples. They do not demonstrate "
            "real RDA accuracy or operational readiness."
        ),
    }

    METRICS_PATH.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print("=" * 60)
    print("RESOURCE REQUIREMENT MODEL — DEMO TEST")
    print("=" * 60)
    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows:  {len(X_test)}")
    print(f"Model saved:   {MODEL_PATH}")
    print(f"Metadata saved: {METRICS_PATH}")
    print("\nTest metrics (simulated data only):")
    for target, values in per_target_metrics.items():
        print(
            f"{target}: MAE={values['mae']:.3f}, "
            f"RMSE={values['rmse']:.3f}"
        )

    print("\nWARNING: These results do not establish real-world accuracy.")


if __name__ == "__main__":
    main()
