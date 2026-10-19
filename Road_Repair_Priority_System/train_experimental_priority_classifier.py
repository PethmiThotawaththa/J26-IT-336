
from pathlib import Path
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier


# ============================================================
# STEP 32 - TRAIN EXPERIMENTAL PRIORITY CLASSIFIER
#
# Target:
# Provisional maintenance / inspection priority
#
# Uses:
# - 9 human-labelled sections
# - All 9 numeric features
# - Decision Tree, max_depth=3
#
# Does NOT modify existing trained models.
# Does NOT modify input CSV files.
# ============================================================


INPUT_FILE = Path(
    "outputs/priority_ml_dataset_experimental.csv"
)

MODEL_FILE = Path(
    "models/experimental_priority_classifier.joblib"
)

FEATURE_COLUMNS = [
    "section_length_m",
    "traffic_mean_vehicles_per_hour",
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "section_forecast_budget_lkr",
    "planned_item_1_count",
    "planned_item_2_count",
    "planned_item_75_count",
]

EXPECTED_LABELS = {
    "B047_0_3680": "High",
    "B047_3680_7420": "High",
    "B174_0_9490": "Low",
    "B214_0_18460": "Medium",
    "B214_18460_28520": "Medium",
    "B240_0_2550": "High",
    "B240_2550_13100": "Low",
    "B263_0_5555": "High",
    "B435_0_7700": "Medium",
}


def heading(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


heading("STEP 32 - EXPERIMENTAL PRIORITY MODEL TRAINING")

# ------------------------------------------------------------
# 1. Check input and output paths
# ------------------------------------------------------------

if not INPUT_FILE.is_file():
    raise FileNotFoundError(
        f"Input dataset not found: {INPUT_FILE}"
    )

# Protect any existing model at the destination.
if MODEL_FILE.exists():
    raise FileExistsError(
        f"Model already exists: {MODEL_FILE}\n"
        "Existing model will NOT be overwritten."
    )

df = pd.read_csv(
    INPUT_FILE,
    dtype={
        "section_id": "string",
        "road_id": "string",
        "priority_label": "string",
    },
)

print("Input dataset:", INPUT_FILE)
print("Dataset rows:", len(df))

# ------------------------------------------------------------
# 2. Validate columns and labels
# ------------------------------------------------------------

required_columns = [
    "section_id",
    "road_id",
    "priority_label",
] + FEATURE_COLUMNS

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )

if len(df) != 9:
    raise ValueError(
        "Expected exactly 9 labelled sections."
    )

for column in [
    "section_id",
    "road_id",
    "priority_label",
]:
    df[column] = df[column].str.strip()

if df["section_id"].isna().any():
    raise ValueError("Missing section IDs.")

if df["section_id"].duplicated().any():
    raise ValueError("Duplicate section IDs.")

if set(df["section_id"]) != set(EXPECTED_LABELS):
    raise ValueError("Unexpected section IDs.")

if df["road_id"].isna().any():
    raise ValueError("Missing road IDs.")

if df["priority_label"].isna().any():
    raise ValueError("Missing human labels.")

if not df["priority_label"].isin(
    ["Low", "Medium", "High"]
).all():
    raise ValueError("Invalid priority labels.")

for section_id, expected_label in EXPECTED_LABELS.items():
    actual_label = df.loc[
        df["section_id"] == section_id,
        "priority_label",
    ].iloc[0]

    if actual_label != expected_label:
        raise ValueError(
            f"Human label changed: {section_id}"
        )

expected_road_ids = (
    df["section_id"].str.split("_").str[0]
)

if not df["road_id"].eq(
    expected_road_ids
).fillna(False).all():
    raise ValueError(
        "road_id does not match section_id."
    )

if df["road_id"].nunique() != 6:
    raise ValueError(
        "Expected 6 independent road groups."
    )

for feature in FEATURE_COLUMNS:
    df[feature] = pd.to_numeric(
        df[feature],
        errors="raise",
    )

X = df[FEATURE_COLUMNS]

if not np.isfinite(
    X.to_numpy(dtype=float)
).all():
    raise ValueError(
        "Missing or invalid numeric feature values."
    )

y = df["priority_label"].to_numpy(dtype=str)

print("\nDataset validation: PASSED")
print("Human labels unchanged: YES")
print("Independent road groups:", df["road_id"].nunique())
print("Features retained:", len(FEATURE_COLUMNS))

print("\nHuman label distribution:")
print(df["priority_label"].value_counts().to_string())

# ------------------------------------------------------------
# 3. Train Decision Tree on all labelled sections
# ------------------------------------------------------------

heading("TRAINING EXPERIMENTAL DECISION TREE")

model = DecisionTreeClassifier(
    max_depth=3,
    random_state=42,
)

model.fit(X, y)

print("Algorithm: DecisionTreeClassifier")
print("max_depth: 3")
print("Training sections:", len(X))
print("Input features:", X.shape[1])
print("Learned classes:", list(model.classes_))

print(
    "\nNOTE: This is a full-data experimental "
    "model, not an independently validated model."
)

print(
    "Previous held-out-road accuracy: "
    "44.44% (4/9)."
)

# ------------------------------------------------------------
# 4. Display feature importance
# ------------------------------------------------------------

heading("EXPLORATORY FEATURE IMPORTANCE")

importance_df = pd.DataFrame({
    "feature": FEATURE_COLUMNS,
    "importance": model.feature_importances_,
}).sort_values(
    "importance",
    ascending=False,
)

print(
    importance_df.to_string(
        index=False,
        float_format=lambda value: f"{value:.4f}",
    )
)

print(
    "\nFeature importance is unstable with "
    "only 9 examples and does not prove causation."
)

# ------------------------------------------------------------
# 5. Save a NEW experimental model file
# ------------------------------------------------------------

heading("SAVE EXPERIMENTAL MODEL")

MODEL_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

model_package = {
    "model": model,
    "feature_columns": FEATURE_COLUMNS,
    "target_name": (
        "provisional_maintenance_inspection_priority"
    ),
    "training_sections": len(df),
    "training_roads": df["road_id"].nunique(),
    "training_section_ids": (
        df["section_id"].astype(str).tolist()
    ),
    "human_label_distribution": (
        df["priority_label"]
        .value_counts()
        .to_dict()
    ),
    "evaluation_note": (
        "Original Decision Tree achieved 4/9 correct "
        "held-out-road predictions in earlier exploratory "
        "Leave-One-Road-Out evaluation. "
        "This is not a reliable real-world accuracy estimate."
    ),
    "created_utc": datetime.now(
        timezone.utc
    ).isoformat(),
}

# Exclusive creation protects existing files.
with MODEL_FILE.open("xb") as output_file:
    joblib.dump(
        model_package,
        output_file,
    )

print("New model saved:", MODEL_FILE)
print("Existing models overwritten: NO")

# ------------------------------------------------------------
# 6. Verify saved model
# ------------------------------------------------------------

heading("VERIFY SAVED MODEL")

loaded_package = joblib.load(MODEL_FILE)

loaded_model = loaded_package["model"]

loaded_features = loaded_package["feature_columns"]

if loaded_features != FEATURE_COLUMNS:
    raise ValueError(
        "Saved feature order does not match."
    )

if loaded_package["target_name"] != (
    "provisional_maintenance_inspection_priority"
):
    raise ValueError(
        "Saved target name does not match."
    )

if loaded_model.n_features_in_ != 9:
    raise ValueError(
        "Saved model does not have 9 features."
    )

test_predictions = loaded_model.predict(
    X.iloc[:2]
)

print("Saved model verification: PASSED")
print("Number of input features: 9")
print("Sample predictions:", list(test_predictions))

heading("FINAL SUMMARY")

print("Supervised ML model trained: YES")
print("All 9 features retained: YES")
print("Human labels used: YES")
print("Automatic labels generated: NO")
print("AI recommendation features used: NO")
print("Input CSV modified: NO")
print("Existing cost model modified: NO")
print("Existing repair-method model modified: NO")
print("New experimental model created: YES")

print(
    "\nIMPORTANT: The model predicts provisional "
    "maintenance / inspection priority, "
    "not verified road repair urgency."
)

print("\nSTEP 32 COMPLETED.")
