
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# STEP 33 - TEST SAVED PRIORITY CLASSIFIER
#
# Purpose:
# Load the previously trained experimental Decision Tree
# and generate provisional maintenance / inspection
# priority predictions.
#
# IMPORTANT:
# - Uses all 9 original numeric input features
# - Includes nearby hospitals, schools and police stations
# - Does not train or modify the saved model
# - Does not modify human labels
# - Does not overwrite existing output files
# - Training-section predictions are NOT independent tests
# ============================================================


MODEL_FILE = Path(
    "models/experimental_priority_classifier.joblib"
)

INPUT_FILE = Path(
    "outputs/priority_ml_dataset_experimental.csv"
)

OUTPUT_FILE = Path(
    "outputs/experimental_priority_predictions.csv"
)

EXPECTED_TARGET = (
    "provisional_maintenance_inspection_priority"
)

EXPECTED_FEATURES = [
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

VALID_LABELS = {
    "Low",
    "Medium",
    "High",
}


def heading(title):
    print()
    print("=" * 75)
    print(title)
    print("=" * 75)


# ============================================================
# 1. CHECK INPUT FILES
# ============================================================

heading("STEP 33 - SAVED PRIORITY MODEL PREDICTION")

if not MODEL_FILE.is_file():
    raise FileNotFoundError(
        f"Saved model not found: {MODEL_FILE}"
    )

if not INPUT_FILE.is_file():
    raise FileNotFoundError(
        f"Input dataset not found: {INPUT_FILE}"
    )

if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"Output already exists: {OUTPUT_FILE}\n"
        "Existing CSV will NOT be overwritten."
    )

print("Saved model:", MODEL_FILE)
print("Input dataset:", INPUT_FILE)
print("Output CSV:", OUTPUT_FILE)


# ============================================================
# 2. LOAD AND VALIDATE SAVED MODEL
# ============================================================

heading("LOAD SAVED EXPERIMENTAL MODEL")

# Only load joblib files created by your own project.
package = joblib.load(MODEL_FILE)

if not isinstance(package, dict):
    raise ValueError(
        "Saved model package must be a dictionary."
    )

required_keys = [
    "model",
    "feature_columns",
    "target_name",
    "training_section_ids",
]

missing_keys = [
    key
    for key in required_keys
    if key not in package
]

if missing_keys:
    raise ValueError(
        f"Missing model metadata: {missing_keys}"
    )

model = package["model"]

feature_columns = package["feature_columns"]

target_name = package["target_name"]

training_section_ids = set(
    package["training_section_ids"]
)

if target_name != EXPECTED_TARGET:
    raise ValueError(
        f"Unexpected target: {target_name}"
    )

if feature_columns != EXPECTED_FEATURES:
    raise ValueError(
        "Saved model feature names or order "
        "do not match the expected 9 features."
    )

if model.n_features_in_ != len(EXPECTED_FEATURES):
    raise ValueError(
        "Saved model feature count mismatch."
    )

if not set(model.classes_).issubset(VALID_LABELS):
    raise ValueError(
        "Saved model has unexpected classes."
    )

print("Model loaded successfully: YES")
print("Target:", target_name)
print("Number of model features:", len(feature_columns))
print("Model classes:", list(model.classes_))

print("\nALL 9 INPUT FEATURES:")

for number, feature in enumerate(
    feature_columns,
    start=1,
):
    print(f"{number}. {feature}")

print(
    "\nNearby important locations included: YES"
)

print(
    "Model retraining performed: NO"
)


# ============================================================
# 3. LOAD PREDICTION DATASET
# ============================================================

heading("LOAD AND VALIDATE PREDICTION INPUT")

df = pd.read_csv(
    INPUT_FILE,
    dtype={
        "section_id": "string",
        "road_id": "string",
        "priority_label": "string",
    },
)

required_columns = [
    "section_id",
    "road_id",
] + feature_columns

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing input columns: {missing_columns}"
    )

if df.empty:
    raise ValueError(
        "Prediction dataset is empty."
    )

df["section_id"] = (
    df["section_id"]
    .astype("string")
    .str.strip()
)

df["road_id"] = (
    df["road_id"]
    .astype("string")
    .str.strip()
)

if df["section_id"].isna().any():
    raise ValueError(
        "Missing section IDs."
    )

if df["road_id"].isna().any():
    raise ValueError(
        "Missing road IDs."
    )

if df["section_id"].duplicated().any():
    raise ValueError(
        "Duplicate section IDs."
    )

expected_road_ids = (
    df["section_id"]
    .str.split("_")
    .str[0]
)

if not df["road_id"].eq(
    expected_road_ids
).fillna(False).all():
    raise ValueError(
        "Road IDs do not match section IDs."
    )

for feature in feature_columns:
    df[feature] = pd.to_numeric(
        df[feature],
        errors="raise",
    )

X = df[feature_columns]

if not np.isfinite(
    X.to_numpy(dtype=float)
).all():
    raise ValueError(
        "Missing or invalid numeric feature values."
    )

print("Input sections:", len(df))
print("Input features:", X.shape[1])
print("Numeric feature validation: PASSED")
print("Feature order matches saved model: YES")


# ============================================================
# 4. GENERATE PREDICTIONS
# ============================================================

heading("GENERATE PRIORITY PREDICTIONS")

predictions = model.predict(X)

if not set(predictions).issubset(VALID_LABELS):
    raise ValueError(
        "Model generated unexpected priority labels."
    )

result = pd.DataFrame({
    "section_id": df["section_id"],
    "road_id": df["road_id"],
    "predicted_provisional_priority": predictions,
    "was_used_for_model_training": (
        df["section_id"].isin(training_section_ids)
    ),
})

# Human labels are included only for reference.
# They are NOT passed to model.predict().

if "priority_label" in df.columns:
    result["human_priority_label"] = (
        df["priority_label"]
    )

result["prediction_target"] = EXPECTED_TARGET

result["model_status"] = (
    "experimental_not_independently_validated"
)

print("\nSECTION-LEVEL PREDICTIONS:")

print(
    result.to_string(
        index=False
    )
)


# ============================================================
# 5. PREDICTION SUMMARY
# ============================================================

heading("PREDICTION SUMMARY")

print("\nPredicted priority distribution:")

print(
    result[
        "predicted_provisional_priority"
    ].value_counts().to_string()
)

training_overlap = int(
    result[
        "was_used_for_model_training"
    ].sum()
)

print(
    "\nSections used during model training:",
    training_overlap
)

print(
    "Total prediction sections:",
    len(result)
)

new_sections = (
    len(result) - training_overlap
)

print(
    "Sections not used during model training:",
    new_sections
)

if training_overlap == len(result):
    print(
        "\nWARNING: All prediction sections "
        "were used to train this model."
    )

    print(
        "These predictions only demonstrate "
        "that the saved model can be loaded "
        "and used successfully."
    )

print(
    "\nIMPORTANT: Predictions on training "
    "sections are NOT independent test results."
)

print(
    "Do not interpret agreement with "
    "training labels as generalization accuracy."
)

print(
    "\nPrevious exploratory held-out-road "
    "Decision Tree result: 4/9 correct (44.44%)."
)

print(
    "That result is separate from this "
    "saved-model prediction test."
)


# ============================================================
# 6. SAVE PREDICTIONS
# ============================================================

heading("SAVE PREDICTION CSV")

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

# Exclusive file creation prevents overwriting.

with OUTPUT_FILE.open(
    "x",
    encoding="utf-8-sig",
    newline="",
) as output_file:

    result.to_csv(
        output_file,
        index=False,
    )

print(
    "Prediction CSV saved:",
    OUTPUT_FILE
)


# ============================================================
# 7. FINAL VERIFICATION SUMMARY
# ============================================================

heading("FINAL SUMMARY")

print("Saved model loaded successfully: YES")
print("Predictions generated: YES")
print("All 9 input features supplied: YES")
print("Nearby hospitals included: YES")
print("Nearby schools included: YES")
print("Nearby police stations included: YES")
print("Human labels used as prediction inputs: NO")
print("Model retrained: NO")
print("Existing trained models modified: NO")
print("Existing input CSV files modified: NO")
print("Existing output files overwritten: NO")

print(
    "\nIMPORTANT RESEARCH LIMITATIONS:"
)

print(
    "- Nearby-location and traffic features "
    "are road-level, not section-specific."
)

print(
    "- Forecast budget is not actual repair cost."
)

print(
    "- Planned maintenance is not verified damage."
)

print(
    "- The model was trained using only "
    "9 human-labelled sections from 6 roads."
)

print(
    "- The target is provisional maintenance / "
    "inspection priority, not verified "
    "road repair urgency."
)

print("\nSTEP 33 COMPLETED.")
