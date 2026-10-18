
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import LeaveOneGroupOut


# -----------------------------------------------
# 1. File paths
# -----------------------------------------------

DATA_PATH = Path("outputs/ml_cost_dataset.csv")

MODEL_PATH = Path(
    "models/experimental_pavement_repair_model.joblib"
)

PREDICTIONS_PATH = Path(
    "outputs/pavement_repair_validation.csv"
)

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------
# 2. RDA pavement repair methods
# -----------------------------------------------

REPAIR_METHODS = {
    1: "Pothole Patching",
    2: "Crack Sealing",
    75: "Section Overlay",
}

FEATURES = [
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
]


# -----------------------------------------------
# 3. Load historical RDA data
# -----------------------------------------------

df = pd.read_csv(DATA_PATH)

df["Item Code"] = pd.to_numeric(
    df["Item Code"],
    errors="coerce",
)

df = df[
    df["Item Code"].isin(REPAIR_METHODS)
].copy()

df = df.dropna(
    subset=["RoadID", "Item Code"]
).reset_index(drop=True)

for feature in FEATURES:
    df[feature] = pd.to_numeric(
        df[feature],
        errors="coerce",
    ).fillna(0)

df["Item Code"] = df["Item Code"].astype(int)

X = df[FEATURES]
y = df["Item Code"]
groups = df["RoadID"]

print("=" * 60)
print("RDA PAVEMENT REPAIR METHOD PREDICTION")
print("=" * 60)

print("\nTotal records:", len(df))
print("Number of roads:", groups.nunique())

print("\nRepair method distribution:")

for code in sorted(REPAIR_METHODS):
    count = (y == code).sum()

    print(
        f"Code {code} - "
        f"{REPAIR_METHODS[code]}: {count}"
    )


# -----------------------------------------------
# 4. Data quality check
# -----------------------------------------------

print("\n" + "=" * 60)
print("DATA QUALITY CHECK")
print("=" * 60)

for code, name in REPAIR_METHODS.items():
    subset = df[df["Item Code"] == code]

    zero_count = (
        subset[FEATURES] == 0
    ).all(axis=1).sum()

    print(
        f"{name}: {zero_count}/{len(subset)} "
        "records have all-zero measurements"
    )

pattern_labels = (
    df.groupby(FEATURES)["Item Code"]
    .nunique()
)

ambiguous_patterns = int(
    (pattern_labels > 1).sum()
)

print(
    "\nMeasurement patterns with multiple labels:",
    ambiguous_patterns,
)

if ambiguous_patterns > 0:
    print(
        "WARNING: Identical input measurements "
        "have different repair method labels."
    )


# -----------------------------------------------
# 5. Extra Trees supervised ML
# -----------------------------------------------

def create_model():
    return ExtraTreesClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )


# -----------------------------------------------
# 6. Leave-One-Road-Out validation
# -----------------------------------------------

print("\n" + "=" * 60)
print("LEAVE-ONE-ROAD-OUT VALIDATION")
print("=" * 60)

logo = LeaveOneGroupOut()

predictions = np.full(
    len(df),
    -1,
    dtype=int,
)

for train_idx, test_idx in logo.split(
    X, y, groups
):

    model = create_model()

    model.fit(
        X.iloc[train_idx],
        y.iloc[train_idx],
    )

    fold_predictions = model.predict(
        X.iloc[test_idx]
    )

    predictions[test_idx] = fold_predictions

    road = groups.iloc[test_idx].iloc[0]

    fold_accuracy = accuracy_score(
        y.iloc[test_idx],
        fold_predictions,
    )

    print(
        f"{road}: "
        f"{fold_accuracy:.2%} "
        f"({len(test_idx)} records)"
    )


# -----------------------------------------------
# 7. Overall model evaluation
# -----------------------------------------------

accuracy = accuracy_score(
    y,
    predictions,
)

macro_f1 = f1_score(
    y,
    predictions,
    labels=sorted(REPAIR_METHODS),
    average="macro",
    zero_division=0,
)

print("\n" + "=" * 60)
print("OVERALL VALIDATION RESULTS")
print("=" * 60)

print(f"Accuracy: {accuracy:.2%}")
print(f"Macro F1 Score: {macro_f1:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y,
        predictions,
        labels=sorted(REPAIR_METHODS),
        target_names=[
            REPAIR_METHODS[code]
            for code in sorted(REPAIR_METHODS)
        ],
        zero_division=0,
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y,
        predictions,
        labels=sorted(REPAIR_METHODS),
    )
)


# -----------------------------------------------
# 8. Save validation predictions
# -----------------------------------------------

results = df[
    ["RoadID", "Item Code"] + FEATURES
].copy()

results["Actual_Method"] = y.map(
    REPAIR_METHODS
)

results["Predicted_Item_Code"] = predictions

results["Predicted_Method"] = [
    REPAIR_METHODS.get(code, "Unknown")
    for code in predictions
]

results["Correct"] = (
    results["Item Code"]
    == results["Predicted_Item_Code"]
)

results.to_csv(
    PREDICTIONS_PATH,
    index=False,
)

print(
    "\nValidation predictions saved:",
    PREDICTIONS_PATH,
)


# -----------------------------------------------
# 9. Train and save final model
# -----------------------------------------------

final_model = create_model()

final_model.fit(X, y)

model_package = {
    "model": final_model,
    "features": FEATURES,
    "repair_methods": REPAIR_METHODS,
    "validation_accuracy": accuracy,
    "validation_macro_f1": macro_f1,
    "status": "EXPERIMENTAL_ONLY",
    "limitation": (
        "Training uses historical RDA maintenance "
        "work measurements rather than independent "
        "pre-repair damage measurements."
    ),
}

joblib.dump(
    model_package,
    MODEL_PATH,
)

print("\nModel saved:", MODEL_PATH)
print("\nTRAINING COMPLETE")
