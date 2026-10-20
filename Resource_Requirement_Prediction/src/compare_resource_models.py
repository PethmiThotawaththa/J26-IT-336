
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import RepeatedKFold
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA_PATH = Path("data/demo/ml_training_data.csv")
OUTPUT_PATH = Path("outputs/demo_model_comparison.csv")

FEATURES = ["repair_type", "quantity", "quantity_unit", "priority"]
TARGETS = [
    "labour_person_days",
    "asphalt_tonnes",
    "aggregate_tonnes",
    "equipment_hours",
]


def make_pipeline(regressor):
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

    return Pipeline([
        ("preprocessing", preprocessing),
        ("regressor", regressor),
    ])


def main():
    df = pd.read_csv(DATA_PATH)

    if set(df["data_status"].astype(str).str.upper()) != {"SIMULATED"}:
        raise ValueError("This comparison accepts SIMULATED data only.")

    if df[FEATURES + TARGETS].isna().any().any():
        raise ValueError("Required data contains missing values.")

    X = df[FEATURES]
    y = df[TARGETS]

    models = {
        "Dummy Baseline": MultiOutputRegressor(
            DummyRegressor(strategy="mean")
        ),
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, random_state=42
        ),
        "Extra Trees": ExtraTreesRegressor(
            n_estimators=200, random_state=42
        ),
    }

    cv = RepeatedKFold(n_splits=4, n_repeats=3, random_state=42)
    scales = y.abs().mean().replace(0, float("nan"))
    rows = []

    for name, regressor in models.items():
        actual_values = {target: [] for target in TARGETS}
        predicted_values = {target: [] for target in TARGETS}

        for train_idx, test_idx in cv.split(X, y):
            pipeline = make_pipeline(regressor)
            pipeline.fit(X.iloc[train_idx], y.iloc[train_idx])
            predictions = pipeline.predict(X.iloc[test_idx])

            for i, target in enumerate(TARGETS):
                actual_values[target].extend(y[target].iloc[test_idx].tolist())
                predicted_values[target].extend(predictions[:, i].tolist())

        for target in TARGETS:
            mae = mean_absolute_error(
                actual_values[target], predicted_values[target]
            )
            rmse = mean_squared_error(
                actual_values[target], predicted_values[target]
            ) ** 0.5

            rows.append({
                "model": name,
                "target": target,
                "mae": float(mae),
                "rmse": float(rmse),
                "scaled_mae": float(mae / scales[target]),
            })

    results = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_PATH, index=False)

    summary = (
        results.groupby("model", as_index=False)
        .agg(mean_scaled_mae=("scaled_mae", "mean"))
        .sort_values("mean_scaled_mae")
    )

    print("=" * 60)
    print("RESOURCE REQUIREMENT MODEL COMPARISON")
    print("=" * 60)
    print(f"Dataset records: {len(df)}")
    print("Data status: SIMULATED")
    print("Evaluation: repeated 4-fold cross-validation, 3 repeats")
    print("\nSummary (lower mean scaled MAE is better):")
    print(summary.to_string(
        index=False, float_format=lambda value: f"{value:.4f}"
    ))
    print("\nDetailed metrics:")
    print(results.to_string(
        index=False, float_format=lambda value: f"{value:.4f}"
    ))
    print(f"\nResults saved to: {OUTPUT_PATH}")
    print("WARNING: Simulated-data comparison only; not validated for RDA use.")


if __name__ == "__main__":
    main()
