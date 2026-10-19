
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd

from sklearn.model_selection import LeaveOneGroupOut
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# ============================================================
# STEP 31 - ALL-FEATURE ML HYPERPARAMETER EXPERIMENT
#
# Target:
# Provisional maintenance / inspection priority
#
# Method:
# Nested Leave-One-Road-Out Cross-Validation
#
# IMPORTANT:
# - ALL 9 selected features are retained
# - Human labels only
# - No automatic label generation
# - No AI recommendation predictors
# - No existing files modified
# - No trained model files saved
# ============================================================


INPUT_FILE = Path(
    "outputs/priority_ml_dataset_experimental.csv"
)

RANDOM_STATE = 42

CLASS_ORDER = [
    "Low",
    "Medium",
    "High",
]

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
# 1. DEFINE MODEL CONFIGURATIONS
# ============================================================

# Every configuration receives all 9 input features.
#
# The model itself may choose to split on only some
# features. That is normal tree-based ML behaviour.
#
# Keep the search space small because the dataset
# contains only 9 labelled sections.


CONFIGURATIONS = [
    {
        "name": "DT_depth1_gini",
        "algorithm": "DecisionTree",
        "max_depth": 1,
        "min_samples_leaf": 1,
        "criterion": "gini",
    },
    {
        "name": "DT_depth2_gini",
        "algorithm": "DecisionTree",
        "max_depth": 2,
        "min_samples_leaf": 1,
        "criterion": "gini",
    },
    {
        "name": "DT_depth3_gini",
        "algorithm": "DecisionTree",
        "max_depth": 3,
        "min_samples_leaf": 1,
        "criterion": "gini",
    },
    {
        "name": "DT_depth2_entropy",
        "algorithm": "DecisionTree",
        "max_depth": 2,
        "min_samples_leaf": 1,
        "criterion": "entropy",
    },
    {
        "name": "DT_depth3_leaf2",
        "algorithm": "DecisionTree",
        "max_depth": 3,
        "min_samples_leaf": 2,
        "criterion": "gini",
    },
    {
        "name": "RF_depth2_leaf1",
        "algorithm": "RandomForest",
        "max_depth": 2,
        "min_samples_leaf": 1,
        "max_features": 1.0,
    },
    {
        "name": "RF_depth3_leaf1",
        "algorithm": "RandomForest",
        "max_depth": 3,
        "min_samples_leaf": 1,
        "max_features": 1.0,
    },
    {
        "name": "RF_depth3_leaf2",
        "algorithm": "RandomForest",
        "max_depth": 3,
        "min_samples_leaf": 2,
        "max_features": 1.0,
    },
    {
        "name": "RF_depth3_sqrt",
        "algorithm": "RandomForest",
        "max_depth": 3,
        "min_samples_leaf": 1,
        "max_features": "sqrt",
    },
]


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================


def heading(title):
    print()
    print("=" * 75)
    print(title)
    print("=" * 75)


def make_model(config):
    """
    Create a fresh model using the supplied settings.
    """

    if config["algorithm"] == "DecisionTree":
        return DecisionTreeClassifier(
            criterion=config["criterion"],
            max_depth=config["max_depth"],
            min_samples_leaf=config["min_samples_leaf"],
            random_state=RANDOM_STATE,
        )

    if config["algorithm"] == "RandomForest":
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=config["max_depth"],
            min_samples_leaf=config["min_samples_leaf"],
            max_features=config["max_features"],
            random_state=RANDOM_STATE,
            n_jobs=1,
        )

    raise ValueError(
        f"Unknown algorithm: {config['algorithm']}"
    )


def calculate_metrics(actual, predictions):
    """
    Calculate metrics from pooled held-out predictions.
    """

    return {
        "accuracy": accuracy_score(
            actual,
            predictions,
        ),
        "balanced_accuracy": balanced_accuracy_score(
            actual,
            predictions,
        ),
        "macro_f1": f1_score(
            actual,
            predictions,
            labels=CLASS_ORDER,
            average="macro",
            zero_division=0,
        ),
        "weighted_f1": f1_score(
            actual,
            predictions,
            labels=CLASS_ORDER,
            average="weighted",
            zero_division=0,
        ),
    }


def label_distribution(labels):
    counts = Counter(labels)

    return ", ".join(
        f"{label}={counts.get(label, 0)}"
        for label in CLASS_ORDER
    )


def inner_road_cv_score(training_df, config):
    """
    Inner cross-validation is performed ONLY on the
    current outer-training roads.

    Outer test-road labels are not used here.
    """

    X_inner = training_df[FEATURE_COLUMNS]

    y_inner = training_df[
        "priority_label"
    ].to_numpy(dtype=str)

    groups_inner = training_df[
        "road_id"
    ].to_numpy(dtype=str)

    splitter = LeaveOneGroupOut()

    predictions = np.empty(
        len(training_df),
        dtype=object,
    )

    prediction_counts = np.zeros(
        len(training_df),
        dtype=int,
    )

    for train_idx, valid_idx in splitter.split(
        X_inner,
        y_inner,
        groups=groups_inner,
    ):

        train_roads = set(
            groups_inner[train_idx]
        )

        valid_roads = set(
            groups_inner[valid_idx]
        )

        if train_roads & valid_roads:
            raise ValueError(
                "Inner road-group leakage detected."
            )

        model = make_model(config)

        model.fit(
            X_inner.iloc[train_idx],
            y_inner[train_idx],
        )

        fold_predictions = model.predict(
            X_inner.iloc[valid_idx]
        )

        predictions[valid_idx] = fold_predictions

        prediction_counts[valid_idx] += 1

    if not np.all(
        prediction_counts == 1
    ):
        raise ValueError(
            "Inner CV prediction count error."
        )

    predictions = np.asarray(
        predictions,
        dtype=str,
    )

    return calculate_metrics(
        y_inner,
        predictions,
    )


# ============================================================
# 3. LOAD DATASET
# ============================================================


heading(
    "STEP 31 - ALL 9 FEATURES HYPERPARAMETER EXPERIMENT"
)

if not INPUT_FILE.is_file():
    raise FileNotFoundError(
        f"Dataset not found: {INPUT_FILE}"
    )

df = pd.read_csv(
    INPUT_FILE,
    dtype={
        "section_id": "string",
        "road_id": "string",
        "priority_label": "string",
    },
)

print("Input file:", INPUT_FILE)
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 4. VALIDATE DATA
# ============================================================


required_columns = [
    "section_id",
    "road_id",
    "priority_label",
] + FEATURE_COLUMNS

missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )

if len(df) != 9:
    raise ValueError(
        f"Expected 9 sections, found {len(df)}."
    )

if df["section_id"].isna().any():
    raise ValueError(
        "Missing section IDs."
    )

if df["section_id"].duplicated().any():
    raise ValueError(
        "Duplicate section IDs."
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

df["priority_label"] = (
    df["priority_label"]
    .astype("string")
    .str.strip()
)

if set(df["section_id"]) != set(
    EXPECTED_HUMAN_LABELS
):
    raise ValueError(
        "Section IDs do not match expected data."
    )

if df["road_id"].isna().any():
    raise ValueError(
        "Missing road IDs."
    )

if not df["priority_label"].isin(
    CLASS_ORDER
).all():
    raise ValueError(
        "Invalid or missing human priority labels."
    )

for section_id, expected_label in (
    EXPECTED_HUMAN_LABELS.items()
):

    actual_label = df.loc[
        df["section_id"] == section_id,
        "priority_label",
    ].iloc[0]

    if actual_label != expected_label:
        raise ValueError(
            f"Human label mismatch for {section_id}."
        )

derived_road_ids = (
    df["section_id"]
    .str.split("_")
    .str[0]
)

if not df["road_id"].eq(
    derived_road_ids
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

if df[FEATURE_COLUMNS].isna().any().any():
    raise ValueError(
        "Missing numeric feature values."
    )

if not np.isfinite(
    df[FEATURE_COLUMNS].to_numpy(
        dtype=float
    )
).all():
    raise ValueError(
        "Non-finite feature values."
    )

print("\nVALIDATION RESULTS:")
print("Dataset validation: PASSED")
print("Human labels verified: YES")
print("Road groups verified: YES")
print("Number of road groups:", df["road_id"].nunique())
print("Numeric predictor features:", len(FEATURE_COLUMNS))

print(
    "AI recommendations excluded from predictors: YES"
)

print(
    "Identifiers excluded from predictors: YES"
)

print(
    "\nHuman label distribution:",
    label_distribution(
        df["priority_label"]
    ),
)


# ============================================================
# 5. VERIFY ALL 9 FEATURES ARE USED
# ============================================================


heading("ALL 9 INPUT FEATURES RETAINED")

for number, feature in enumerate(
    FEATURE_COLUMNS,
    start=1,
):
    print(f"{number}. {feature}")

print(
    "\nEvery candidate model receives "
    "all 9 input features."
)

print(
    "No feature selection or feature "
    "removal is performed."
)

print(
    "\nNOTE: Tree algorithms can internally "
    "use only some features for splits."
)


# ============================================================
# 6. DISPLAY MODEL CONFIGURATIONS
# ============================================================


heading("HYPERPARAMETER CONFIGURATIONS")

print(
    "Total configurations:",
    len(CONFIGURATIONS),
)

for config in CONFIGURATIONS:
    print(
        f"- {config['name']}"
    )

print(
    "\nModel configurations are evaluated "
    "using only training-road data "
    "inside each outer fold."
)


# ============================================================
# 7. OUTER LEAVE-ONE-ROAD-OUT EVALUATION
# ============================================================


heading("NESTED ROAD-GROUP-AWARE EVALUATION")

outer_cv = LeaveOneGroupOut()

X = df[FEATURE_COLUMNS]

y = df[
    "priority_label"
].to_numpy(dtype=str)

groups = df[
    "road_id"
].to_numpy(dtype=str)

section_ids = df[
    "section_id"
].to_numpy(dtype=str)

outer_splits = list(
    outer_cv.split(
        X,
        y,
        groups=groups,
    )
)

if len(outer_splits) != 6:
    raise ValueError(
        "Expected exactly 6 outer folds."
    )

nested_predictions = np.empty(
    len(df),
    dtype=object,
)

baseline_predictions = np.empty(
    len(df),
    dtype=object,
)

nested_counts = np.zeros(
    len(df),
    dtype=int,
)

baseline_counts = np.zeros(
    len(df),
    dtype=int,
)

selected_configurations = []


# ============================================================
# 8. TRAIN / VALIDATE / TEST
# ============================================================


for fold_number, (
    train_idx,
    test_idx,
) in enumerate(
    outer_splits,
    start=1,
):

    training_df = df.iloc[
        train_idx
    ].copy()

    testing_df = df.iloc[
        test_idx
    ].copy()

    train_roads = set(
        training_df["road_id"]
    )

    test_roads = set(
        testing_df["road_id"]
    )

    if train_roads & test_roads:
        raise ValueError(
            "Outer road-group leakage detected."
        )

    if len(test_roads) != 1:
        raise ValueError(
            "Expected one held-out road per fold."
        )

    held_out_road = sorted(
        test_roads
    )[0]

    print("\n" + "-" * 75)

    print(
        f"OUTER FOLD {fold_number}: "
        f"TEST ROAD = {held_out_road}"
    )

    print("-" * 75)

    print(
        "Training sections:",
        len(train_idx),
    )

    print(
        "Testing sections:",
        len(test_idx),
    )

    print(
        "Training roads:",
        len(train_roads),
    )

    print(
        "Training labels:",
        label_distribution(
            training_df["priority_label"]
        ),
    )

    # --------------------------------------------------------
    # INNER MODEL SELECTION
    # --------------------------------------------------------

    inner_results = []

    for config in CONFIGURATIONS:

        metrics = inner_road_cv_score(
            training_df,
            config,
        )

        inner_results.append(
            {
                "config": config,
                "macro_f1": metrics["macro_f1"],
                "balanced_accuracy": (
                    metrics["balanced_accuracy"]
                ),
                "accuracy": metrics["accuracy"],
            }
        )

    # Highest inner Macro F1 is preferred.
    # Other metrics break ties.
    # Final ties keep the earlier predefined model.

    selected_result = max(
        inner_results,
        key=lambda result: (
            result["macro_f1"],
            result["balanced_accuracy"],
            result["accuracy"],
        ),
    )

    selected_config = selected_result[
        "config"
    ]

    print(
        "\nSelected configuration:",
        selected_config["name"],
    )

    print(
        "Inner Macro F1:",
        f"{selected_result['macro_f1']:.4f}",
    )

    print(
        "Inner Balanced Accuracy:",
        f"{selected_result['balanced_accuracy']:.4f}",
    )

    # --------------------------------------------------------
    # TRAIN SELECTED MODEL
    # --------------------------------------------------------

    selected_model = make_model(
        selected_config
    )

    selected_model.fit(
        training_df[FEATURE_COLUMNS],
        training_df[
            "priority_label"
        ].to_numpy(dtype=str),
    )

    selected_fold_predictions = (
        selected_model.predict(
            testing_df[FEATURE_COLUMNS]
        )
    )

    nested_predictions[
        test_idx
    ] = selected_fold_predictions

    nested_counts[
        test_idx
    ] += 1

    # --------------------------------------------------------
    # ORIGINAL STEP 29 DECISION TREE BASELINE
    # --------------------------------------------------------

    baseline_model = DecisionTreeClassifier(
        max_depth=3,
        min_samples_leaf=1,
        random_state=RANDOM_STATE,
    )

    baseline_model.fit(
        training_df[FEATURE_COLUMNS],
        training_df[
            "priority_label"
        ].to_numpy(dtype=str),
    )

    baseline_fold_predictions = (
        baseline_model.predict(
            testing_df[FEATURE_COLUMNS]
        )
    )

    baseline_predictions[
        test_idx
    ] = baseline_fold_predictions

    baseline_counts[
        test_idx
    ] += 1

    selected_configurations.append(
        {
            "road": held_out_road,
            "config": selected_config["name"],
            "inner_macro_f1": (
                selected_result["macro_f1"]
            ),
        }
    )

    print("\nHELD-OUT ROAD PREDICTIONS:")

    for local_index, row_index in enumerate(
        test_idx
    ):

        print(
            f"  {section_ids[row_index]}"
            f" | Human: {y[row_index]}"
            f" | Tuned: "
            f"{selected_fold_predictions[local_index]}"
            f" | Original DT: "
            f"{baseline_fold_predictions[local_index]}"
        )


# ============================================================
# 9. SAFETY CHECKS
# ============================================================


heading("CROSS-VALIDATION SAFETY CHECK")

if not np.all(
    nested_counts == 1
):
    raise ValueError(
        "Not all nested predictions tested once."
    )

if not np.all(
    baseline_counts == 1
):
    raise ValueError(
        "Not all baseline predictions tested once."
    )

nested_predictions = np.asarray(
    nested_predictions,
    dtype=str,
)

baseline_predictions = np.asarray(
    baseline_predictions,
    dtype=str,
)

if not set(
    nested_predictions
).issubset(CLASS_ORDER):
    raise ValueError(
        "Invalid tuned model predictions."
    )

if not set(
    baseline_predictions
).issubset(CLASS_ORDER):
    raise ValueError(
        "Invalid baseline predictions."
    )

print(
    "Each road tested separately: YES"
)

print(
    "Each section tested exactly once: YES"
)

print(
    "Road group leakage detected: NO"
)

print(
    "Outer test labels used for tuning: NO"
)

print(
    "All 9 features retained: YES"
)


# ============================================================
# 10. COMPARE ACCURACY AND F1
# ============================================================


heading("ORIGINAL VS TUNED MODEL COMPARISON")

baseline_metrics = calculate_metrics(
    y,
    baseline_predictions,
)

tuned_metrics = calculate_metrics(
    y,
    nested_predictions,
)

results_df = pd.DataFrame(
    [
        {
            "Method": "Original Decision Tree",
            **baseline_metrics,
        },
        {
            "Method": "Nested Hyperparameter Tuning",
            **tuned_metrics,
        },
    ]
)

print(
    results_df.to_string(
        index=False,
        float_format=lambda value: f"{value:.4f}",
    )
)

baseline_correct = int(
    np.sum(
        y == baseline_predictions
    )
)

tuned_correct = int(
    np.sum(
        y == nested_predictions
    )
)

print(
    f"\nOriginal correct: {baseline_correct}/9"
)

print(
    f"Tuned correct: {tuned_correct}/9"
)

accuracy_difference = (
    tuned_metrics["accuracy"]
    - baseline_metrics["accuracy"]
)

print(
    "\nAccuracy difference:",
    f"{accuracy_difference:+.4f}",
)

if accuracy_difference > 0:
    print(
        "\nRESULT: Observed accuracy improvement."
    )

elif accuracy_difference < 0:
    print(
        "\nRESULT: Tuned method scored lower "
        "than the original model."
    )

else:
    print(
        "\nRESULT: No accuracy difference."
    )

print(
    "\nIMPORTANT: This experiment does not "
    "prove reliable real-world improvement."
)


# ============================================================
# 11. CONFUSION MATRICES
# ============================================================


heading("CONFUSION MATRICES")

for model_name, predictions in [
    (
        "Original Decision Tree",
        baseline_predictions,
    ),
    (
        "Nested Tuned Model",
        nested_predictions,
    ),
]:

    print(
        "\nALGORITHM:",
        model_name,
    )

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

    print(
        "\n",
        matrix_df.to_string(),
    )

    print(
        "\nCLASSIFICATION REPORT:"
    )

    print(
        classification_report(
            y,
            predictions,
            labels=CLASS_ORDER,
            zero_division=0,
        )
    )


# ============================================================
# 12. SELECTED CONFIGURATIONS
# ============================================================


heading("SELECTED CONFIGURATIONS BY ROAD")

for item in selected_configurations:

    print(
        f"Road: {item['road']}"
        f" | Configuration: {item['config']}"
        f" | Inner Macro F1: "
        f"{item['inner_macro_f1']:.4f}"
    )

print(
    "\nCONFIGURATION SELECTION FREQUENCY:"
)

counts = Counter(
    item["config"]
    for item in selected_configurations
)

for name, count in counts.items():
    print(
        f"{name}: {count}"
    )


# ============================================================
# 13. SECTION-LEVEL PREDICTIONS
# ============================================================


heading("SECTION-LEVEL HELD-OUT PREDICTIONS")

prediction_table = pd.DataFrame(
    {
        "section_id": section_ids,
        "road_id": groups,
        "human_label": y,
        "original_DT": baseline_predictions,
        "nested_tuned": nested_predictions,
    }
)

print(
    "\n"
    + prediction_table.to_string(
        index=False
    )
)


# ============================================================
# 14. RESEARCH INTERPRETATION
# ============================================================


heading("RESEARCH INTERPRETATION")

print("\n1. SUPERVISED MACHINE LEARNING")

print(
    "Decision Tree and Random Forest "
    "were trained on manually assigned "
    "human priority labels."
)

print("\n2. ALL FEATURES RETAINED")

print(
    "Every model received the same "
    "9 numeric predictor features."
)

print("\n3. HYPERPARAMETER TUNING")

print(
    "Tree depth, minimum leaf size, "
    "splitting criterion and Random Forest "
    "feature-sampling settings were compared."
)

print("\n4. NESTED EVALUATION")

print(
    "Inner folds selected configurations "
    "using training roads only."
)

print(
    "Outer folds tested the selected "
    "configuration on a held-out road."
)

print("\n5. LIMITED DATA")

print(
    "Only 9 labelled sections from "
    "6 independent roads were available."
)

print(
    "The scores cannot establish "
    "reliable generalization accuracy."
)

print("\n6. ROAD-LEVEL FEATURES")

print(
    "Traffic and nearby-location values "
    "are road-level, repeated across sections."
)

print("\n7. BUDGET")

print(
    "Forecast maintenance budget is "
    "not actual road repair cost."
)

print("\n8. PLANNED WORK")

print(
    "Planned pavement maintenance items "
    "are not verified road damage."
)

print("\n9. TARGET")

print(
    "The target remains provisional "
    "maintenance / inspection priority, "
    "not verified road repair urgency."
)

print("\n10. ANNOTATION LIMITATION")

print(
    "AI recommendations were visible "
    "during human annotation."
)

print(
    "The human labels were therefore "
    "not fully AI-blinded."
)

print("\n11. MODEL SELECTION LIMITATION")

print(
    "Earlier exploratory analysis "
    "already inspected all 9 labels."
)

print(
    "This is not a fully independent "
    "external evaluation."
)

print(
    "Repeated tuning on the same small "
    "dataset may overfit the evaluation."
)

print("\n12. NEXT REQUIREMENT")

print(
    "Collect more independently "
    "human-labelled road sections, "
    "preferably with observed damage "
    "severity information."
)

print(
    "\nNO AUTOMATIC LABELS GENERATED."
)

print(
    "NO EXISTING CSV FILES MODIFIED."
)

print(
    "NO EXISTING TRAINED MODELS MODIFIED."
)

print(
    "NO MODEL FILES SAVED."
)

print(
    "\nSTEP 31 COMPLETED."
)
