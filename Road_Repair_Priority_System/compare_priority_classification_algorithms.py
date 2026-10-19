
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd

from sklearn.model_selection import LeaveOneGroupOut
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
)
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# ============================================================
# STEP 29 - SUPERVISED ML ALGORITHM COMPARISON
#
# Target:
# Provisional maintenance / inspection priority
#
# Evaluation:
# Leave-One-Road-Out cross-validation
#
# SAFETY:
# - Human labels only
# - No automatic target generation
# - No AI recommendation features
# - No existing file overwrites
# - No trained model files saved
# ============================================================


INPUT_FILE = Path(
    "outputs/priority_ml_dataset_experimental.csv"
)

RANDOM_STATE = 42

CLASS_ORDER = ["Low", "Medium", "High"]

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

TARGET_COLUMN = "priority_label"
GROUP_COLUMN = "road_id"

EXPECTED_HUMAN_LABELS = {
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


# ============================================================
# 1. HELPER FUNCTIONS
# ============================================================


def separator():
    print("=" * 75)


def make_models():
    """
    Fresh model objects for each evaluation fold.

    All models are supervised classifiers except
    Dummy Baseline, which is a reference benchmark.
    """

    return {
        "Dummy Baseline": DummyClassifier(
            strategy="most_frequent"
        ),

        "Decision Tree": DecisionTreeClassifier(
            max_depth=3,
            min_samples_leaf=1,
            random_state=RANDOM_STATE,
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=3,
            min_samples_leaf=1,
            random_state=RANDOM_STATE,
            n_jobs=1,
        ),

        "Extra Trees": ExtraTreesClassifier(
            n_estimators=100,
            max_depth=3,
            min_samples_leaf=1,
            random_state=RANDOM_STATE,
            n_jobs=1,
        ),
    }


def format_distribution(values):
    counts = Counter(values)

    return ", ".join(
        f"{label}={counts.get(label, 0)}"
        for label in CLASS_ORDER
    )


# ============================================================
# 2. LOAD DATA
# ============================================================

separator()
print("STEP 29 - SUPERVISED ML ALGORITHM COMPARISON")
separator()

print("\nInput file:", INPUT_FILE)

if not INPUT_FILE.is_file():
    raise FileNotFoundError(
        f"Input dataset not found: {INPUT_FILE}"
    )

df = pd.read_csv(
    INPUT_FILE,
    dtype={
        "section_id": "string",
        "road_id": "string",
    },
)

print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 3. VALIDATE INPUT STRUCTURE
# ============================================================

required_columns = [
    "section_id",
    GROUP_COLUMN,
    TARGET_COLUMN,
] + FEATURE_COLUMNS

missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

if len(df) != 9:
    raise ValueError(
        f"Expected 9 sections, found {len(df)}."
    )

if df["section_id"].isna().any():
    raise ValueError("Missing section IDs.")

if df["section_id"].duplicated().any():
    raise ValueError("Duplicate section IDs.")

if set(df["section_id"]) != set(
    EXPECTED_HUMAN_LABELS
):
    raise ValueError(
        "Section IDs do not match expected sections."
    )

df[TARGET_COLUMN] = (
    df[TARGET_COLUMN]
    .astype("string")
    .str.strip()
)

df[GROUP_COLUMN] = (
    df[GROUP_COLUMN]
    .astype("string")
    .str.strip()
)

if df[GROUP_COLUMN].isna().any():
    raise ValueError("Missing road groups.")

if not df[TARGET_COLUMN].isin(
    CLASS_ORDER
).all():
    raise ValueError(
        "Invalid or missing human priority labels."
    )


# ============================================================
# 4. VERIFY ALL HUMAN LABELS
# ============================================================

for section_id, expected_label in (
    EXPECTED_HUMAN_LABELS.items()
):

    actual_label = df.loc[
        df["section_id"] == section_id,
        TARGET_COLUMN,
    ].iloc[0]

    if actual_label != expected_label:
        raise ValueError(
            f"Human label mismatch: {section_id}. "
            f"Expected {expected_label}; "
            f"found {actual_label}."
        )

derived_road_ids = (
    df["section_id"]
    .str.split("_")
    .str[0]
)

if not df[GROUP_COLUMN].eq(
    derived_road_ids
).fillna(False).all():
    raise ValueError(
        "road_id does not match section_id."
    )

if df[GROUP_COLUMN].nunique() != 6:
    raise ValueError(
        "Expected exactly 6 road groups."
    )

print("\nHuman labels verified: YES")
print("Road groups verified: YES")


# ============================================================
# 5. EXPLICIT LEAKAGE PROTECTION
# ============================================================

prohibited_features = {
    "section_id",
    "road_id",
    "priority_label",
    "annotation_reason",
    "annotation_confidence",
    "annotation_target",
    "ai_recommendation",
    "ai_recommendation_confidence",
    "additional_observations",
    "evidence_reviewed",
    "damage_severity_status",
}

leakage_columns = (
    set(FEATURE_COLUMNS)
    & prohibited_features
)

if leakage_columns:
    raise ValueError(
        "Prohibited predictors detected: "
        f"{sorted(leakage_columns)}"
    )

print("AI / annotation feature leakage: NOT DETECTED")
print("Identifiers excluded from predictors: YES")


# ============================================================
# 6. PREPARE NUMERIC FEATURES
# ============================================================

X = df[FEATURE_COLUMNS].copy()

for col in FEATURE_COLUMNS:
    X[col] = pd.to_numeric(
        X[col],
        errors="raise",
    )

if X.isna().any().any():
    raise ValueError(
        "Missing numeric predictor values detected."
    )

if not np.isfinite(
    X.to_numpy(dtype=float)
).all():
    raise ValueError(
        "Non-finite numeric predictor values detected."
    )

y = df[TARGET_COLUMN].to_numpy(
    dtype=str
)

groups = df[GROUP_COLUMN].to_numpy(
    dtype=str
)

section_ids = df["section_id"].to_numpy(
    dtype=str
)

print("\nNumeric features:", len(FEATURE_COLUMNS))
print("Sections:", len(df))
print("Road groups:", len(np.unique(groups)))

print("\nHUMAN LABEL DISTRIBUTION:")
print(format_distribution(y))

print("\nSELECTED FEATURES:")

for feature in FEATURE_COLUMNS:
    print("-", feature)


# ============================================================
# 7. LEAVE-ONE-ROAD-OUT CROSS-VALIDATION
# ============================================================

separator()
print("ROAD-GROUP-AWARE CROSS-VALIDATION")
separator()

logo = LeaveOneGroupOut()

splits = list(
    logo.split(
        X,
        y,
        groups=groups,
    )
)

print("\nNumber of evaluation folds:", len(splits))

if len(splits) != 6:
    raise ValueError(
        "Unexpected number of road-group folds."
    )

model_names = list(make_models().keys())

all_predictions = {
    name: np.empty(
        len(df),
        dtype=object,
    )
    for name in model_names
}

all_prediction_counts = {
    name: np.zeros(
        len(df),
        dtype=int,
    )
    for name in model_names
}

fold_details = {
    name: []
    for name in model_names
}


# ============================================================
# 8. TRAIN AND TEST EACH ALGORITHM
# ============================================================

for fold_number, (
    train_idx,
    test_idx,
) in enumerate(splits, start=1):

    train_roads = set(
        groups[train_idx]
    )

    test_roads = set(
        groups[test_idx]
    )

    # Critical group-leakage check:
    if train_roads & test_roads:
        raise ValueError(
            "Road group leakage detected!"
        )

    if len(test_roads) != 1:
        raise ValueError(
            "Each fold must hold out exactly one road."
        )

    held_out_road = sorted(
        test_roads
    )[0]

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y[train_idx]
    y_test = y[test_idx]

    print("\n" + "-" * 75)
    print(
        f"FOLD {fold_number}: "
        f"TEST ROAD = {held_out_road}"
    )
    print("-" * 75)

    print("Training sections:", len(train_idx))
    print("Testing sections:", len(test_idx))
    print("Training road groups:", len(train_roads))

    print(
        "Training label distribution:",
        format_distribution(y_train),
    )

    print(
        "Testing label distribution:",
        format_distribution(y_test),
    )

    if len(set(y_test)) < 3:
        print(
            "WARNING: This test fold does not "
            "contain all three priority classes."
        )

    if len(set(y_train)) < 3:
        print(
            "WARNING: Training fold is missing "
            "one or more priority classes."
        )

    # Fresh classifiers for every fold.
    models = make_models()

    for model_name, model in models.items():

        # Actual supervised training happens here.
        model.fit(
            X_train,
            y_train,
        )

        predictions = model.predict(
            X_test
        )

        all_predictions[
            model_name
        ][test_idx] = predictions

        all_prediction_counts[
            model_name
        ][test_idx] += 1

        fold_accuracy = accuracy_score(
            y_test,
            predictions,
        )

        fold_details[
            model_name
        ].append(
            {
                "fold": fold_number,
                "road": held_out_road,
                "test_sections": len(test_idx),
                "accuracy": fold_accuracy,
            }
        )

        print(
            f"\n{model_name}"
            f"\n  Fold accuracy: "
            f"{fold_accuracy:.4f}"
        )

        for local_idx, row_idx in enumerate(
            test_idx
        ):

            print(
                f"  {section_ids[row_idx]} "
                f"| Actual: {y_test[local_idx]} "
                f"| Predicted: "
                f"{predictions[local_idx]}"
            )


# ============================================================
# 9. VERIFY ALL SECTIONS WERE TESTED ONCE
# ============================================================

separator()
print("CROSS-VALIDATION SAFETY CHECK")
separator()

for model_name in model_names:

    counts = all_prediction_counts[
        model_name
    ]

    if not np.all(counts == 1):
        raise ValueError(
            f"{model_name}: Not every section "
            "received exactly one held-out prediction."
        )

    predictions = all_predictions[
        model_name
    ]

    if any(
        prediction is None
        for prediction in predictions
    ):
        raise ValueError(
            f"{model_name}: Missing prediction."
        )

    print(
        f"{model_name}: "
        "Each section tested exactly once - PASS"
    )


# ============================================================
# 10. COMPARE ALGORITHMS
# ============================================================

separator()
print("EXPLORATORY ALGORITHM COMPARISON")
separator()

results = []

for model_name in model_names:

    predictions = np.asarray(
        all_predictions[model_name],
        dtype=str,
    )

    accuracy = accuracy_score(
        y,
        predictions,
    )

    balanced_accuracy = (
        balanced_accuracy_score(
            y,
            predictions,
        )
    )

    macro_f1 = f1_score(
        y,
        predictions,
        labels=CLASS_ORDER,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y,
        predictions,
        labels=CLASS_ORDER,
        average="weighted",
        zero_division=0,
    )

    results.append(
        {
            "Algorithm": model_name,
            "Accuracy": accuracy,
            "Balanced Accuracy": balanced_accuracy,
            "Macro F1": macro_f1,
            "Weighted F1": weighted_f1,
        }
    )

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    by=[
        "Macro F1",
        "Balanced Accuracy",
        "Accuracy",
    ],
    ascending=False,
    kind="stable",
)

print(
    "\nPooled held-out predictions "
    "from 6 road-group folds:\n"
)

print(
    results_df.to_string(
        index=False,
        float_format=lambda value: f"{value:.4f}",
    )
)

print(
    "\nIMPORTANT: These scores are descriptive "
    "feasibility results, not reliable "
    "generalization accuracy estimates."
)


# ============================================================
# 11. CONFUSION MATRIX AND CLASS REPORT
# ============================================================

separator()
print("DETAILED CLASSIFICATION REPORTS")
separator()

for model_name in model_names:

    predictions = np.asarray(
        all_predictions[model_name],
        dtype=str,
    )

    print("\n" + "-" * 75)
    print("ALGORITHM:", model_name)
    print("-" * 75)

    matrix = confusion_matrix(
        y,
        predictions,
        labels=CLASS_ORDER,
    )

    matrix_df = pd.DataFrame(
        matrix,
        index=[
            f"Actual_{label}"
            for label in CLASS_ORDER
        ],
        columns=[
            f"Predicted_{label}"
            for label in CLASS_ORDER
        ],
    )

    print("\nCONFUSION MATRIX:")
    print(matrix_df.to_string())

    print("\nCLASSIFICATION REPORT:")

    print(
        classification_report(
            y,
            predictions,
            labels=CLASS_ORDER,
            zero_division=0,
        )
    )


# ============================================================
# 12. SHOW FOLD-BY-FOLD RESULTS
# ============================================================

separator()
print("ROAD-BY-ROAD PERFORMANCE")
separator()

for model_name in model_names:

    print("\nALGORITHM:", model_name)

    for detail in fold_details[
        model_name
    ]:

        print(
            f"  Road: {detail['road']}"
            f" | Test sections: "
            f"{detail['test_sections']}"
            f" | Fold accuracy: "
            f"{detail['accuracy']:.4f}"
        )


# ============================================================
# 13. SHOW ALL HELD-OUT PREDICTIONS
# ============================================================

separator()
print("SECTION-LEVEL HELD-OUT PREDICTIONS")
separator()

prediction_table = pd.DataFrame(
    {
        "section_id": section_ids,
        "road_id": groups,
        "human_label": y,
    }
)

for model_name in model_names:

    prediction_table[
        model_name
    ] = all_predictions[
        model_name
    ]

print(
    "\n"
    + prediction_table.to_string(
        index=False
    )
)


# ============================================================
# 14. EXPERIMENT INTERPRETATION
# ============================================================

separator()
print("RESEARCH INTERPRETATION AND LIMITATIONS")
separator()

print("\n1. SUPERVISED LEARNING")
print(
    "Decision Tree, Random Forest and Extra Trees "
    "were trained using manually assigned "
    "human priority labels."
)

print("\n2. EVALUATION METHOD")
print(
    "Leave-One-Road-Out cross-validation "
    "was used."
)

print(
    "Sections from the same road were never "
    "split between training and testing "
    "within the same fold."
)

print("\n3. SMALL DATASET")
print(
    "Only 9 labelled sections from 6 roads "
    "are available."
)

print(
    "Scores are highly sensitive to individual "
    "predictions and cannot establish "
    "reliable generalization."
)

print("\n4. INCOMPLETE CLASS COVERAGE")
print(
    "Some held-out road folds contain only "
    "one priority class."
)

print(
    "Per-fold accuracy is therefore "
    "not a stable measure of performance."
)

print("\n5. ROAD-LEVEL FEATURES")
print(
    "Traffic and nearby-location features "
    "are road-level values repeated "
    "across sections."
)

print("\n6. BUDGET AND PLANNED WORK")
print(
    "Forecast maintenance budget is not "
    "actual repair cost."
)

print(
    "Planned pavement work is not "
    "verified road damage."
)

print("\n7. TARGET MEANING")
print(
    "The target is provisional maintenance "
    "/ inspection priority, not "
    "verified road repair urgency."
)

print("\n8. ANNOTATION LIMITATION")
print(
    "AI recommendations were visible "
    "during human annotation."
)

print(
    "Therefore, the human labels cannot "
    "be described as fully AI-blinded."
)

print("\n9. ALGORITHM RANKING")
print(
    "Any ranking shown above is exploratory "
    "only. It does not prove that one "
    "algorithm is generally superior."
)

print("\n10. NEXT RESEARCH REQUIREMENT")
print(
    "Collect additional independently "
    "labelled road sections, ideally "
    "with observed damage severity."
)

print("\n11. MODEL FILES")
print(
    "No final model files were saved "
    "or modified during this experiment."
)

print("\nNO AUTOMATIC LABELS GENERATED.")
print("NO EXISTING CSV FILES MODIFIED.")
print("NO EXISTING TRAINED MODELS MODIFIED.")

print("\nSTEP 29 COMPLETED.")
