
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# STEP 30 - PRIORITY ML FEATURE ANALYSIS
#
# Purpose:
# Investigate the experimental dataset before
# attempting model improvements.
#
# This script:
# - Reads the existing experimental dataset
# - Checks numeric feature quality
# - Detects repeated / constant feature values
# - Checks feature relationships
# - Inspects human-label patterns
# - Identifies potential modelling difficulties
#
# SAFETY:
# - No model training
# - No automatic labels
# - No input file modification
# - No existing model modification
# ============================================================


INPUT_FILE = Path(
    "outputs/priority_ml_dataset_experimental.csv"
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

ROAD_LEVEL_FEATURES = [
    "traffic_mean_vehicles_per_hour",
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
]

CLASS_ORDER = [
    "Low",
    "Medium",
    "High",
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


def heading(title):
    print()
    print("=" * 75)
    print(title)
    print("=" * 75)


def print_table(table):
    print(
        table.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )


# ============================================================
# 1. LOAD DATASET
# ============================================================

heading("STEP 30 - PRIORITY ML FEATURE ANALYSIS")

if not INPUT_FILE.is_file():
    raise FileNotFoundError(
        f"Dataset not found: {INPUT_FILE}"
    )

df = pd.read_csv(
    INPUT_FILE,
    dtype={
        "section_id": "string",
        "road_id": "string",
    },
)

print("Input file:", INPUT_FILE)
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 2. VALIDATE DATASET
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
        "Expected exactly 9 labelled sections."
    )

if df["section_id"].isna().any():
    raise ValueError("Missing section IDs.")

if df["section_id"].duplicated().any():
    raise ValueError("Duplicate section IDs.")

if set(df["section_id"]) != set(
    EXPECTED_HUMAN_LABELS
):
    raise ValueError(
        "Unexpected section IDs detected."
    )

df["priority_label"] = (
    df["priority_label"]
    .astype("string")
    .str.strip()
)

df["road_id"] = (
    df["road_id"]
    .astype("string")
    .str.strip()
)

if df["road_id"].isna().any():
    raise ValueError("Missing road IDs.")

if not df["priority_label"].isin(
    CLASS_ORDER
).all():
    raise ValueError(
        "Invalid or missing priority labels."
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
            f"Human label changed for {section_id}."
        )

derived_roads = (
    df["section_id"]
    .str.split("_")
    .str[0]
)

if not df["road_id"].eq(
    derived_roads
).fillna(False).all():
    raise ValueError(
        "road_id and section_id do not match."
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
        "Missing feature values detected."
    )

if not np.isfinite(
    df[FEATURE_COLUMNS].to_numpy(
        dtype=float
    )
).all():
    raise ValueError(
        "Non-finite feature values detected."
    )

print("\nDataset validation: PASSED")
print("Human labels unchanged: YES")
print("Road groups:", df["road_id"].nunique())
print("Numeric features:", len(FEATURE_COLUMNS))


# ============================================================
# 3. CLASS DISTRIBUTION
# ============================================================

heading("HUMAN PRIORITY LABEL DISTRIBUTION")

distribution = (
    df["priority_label"]
    .value_counts()
    .reindex(
        CLASS_ORDER,
        fill_value=0,
    )
)

print(distribution.to_string())

print(
    "\nNOTE: The smallest class contains "
    f"{distribution.min()} examples."
)


# ============================================================
# 4. FEATURE STATISTICS
# ============================================================

heading("NUMERIC FEATURE STATISTICS")

statistics = []

for feature in FEATURE_COLUMNS:

    values = df[feature]

    statistics.append(
        {
            "feature": feature,
            "unique_values": values.nunique(),
            "minimum": values.min(),
            "maximum": values.max(),
            "mean": values.mean(),
            "std_dev": values.std(),
        }
    )

stats_df = pd.DataFrame(statistics)

print_table(stats_df)


# ============================================================
# 5. CONSTANT / LOW-VARIATION FEATURES
# ============================================================

heading("FEATURE VARIATION CHECK")

constant_features = []

low_variation_features = []

for feature in FEATURE_COLUMNS:

    unique_count = df[feature].nunique()

    if unique_count == 1:
        constant_features.append(feature)

    elif unique_count <= 2:
        low_variation_features.append(feature)

if constant_features:
    print("\nConstant features:")

    for feature in constant_features:
        print("-", feature)
else:
    print("\nNo fully constant features detected.")

if low_variation_features:
    print("\nFeatures with only 2 distinct values:")

    for feature in low_variation_features:
        print("-", feature)
else:
    print("\nNo two-value features detected.")

print(
    "\nNOTE: Low variation does not automatically "
    "mean a feature is useless."
)


# ============================================================
# 6. ROAD-LEVEL FEATURE REPETITION
# ============================================================

heading("ROAD-LEVEL FEATURE REPETITION")

print(
    "\nTraffic and nearby-location features "
    "are road-level measurements."
)

print(
    "Sections belonging to the same road "
    "may therefore share these values."
)

road_feature_variation = (
    df.groupby("road_id")[
        ROAD_LEVEL_FEATURES
    ]
    .nunique()
)

print(
    "\nDistinct values within each road:\n"
)

print(
    road_feature_variation.to_string()
)

repeated_on_every_road = [
    feature
    for feature in ROAD_LEVEL_FEATURES
    if (
        road_feature_variation[feature] <= 1
    ).all()
]

print(
    "\nRoad-level features constant "
    "within every road:"
)

for feature in repeated_on_every_road:
    print("-", feature)

print(
    "\nIMPORTANT: These are not independent "
    "section-level observations."
)


# ============================================================
# 7. FEATURE CORRELATION
# ============================================================

heading("FEATURE CORRELATION ANALYSIS")

correlation_matrix = (
    df[FEATURE_COLUMNS]
    .corr(method="spearman")
)

print(
    "\nSpearman feature correlation matrix:\n"
)

print(
    correlation_matrix.to_string(
        float_format=lambda x: f"{x:.3f}"
    )
)

strong_pairs = []

for i, feature_a in enumerate(
    FEATURE_COLUMNS
):

    for feature_b in FEATURE_COLUMNS[
        i + 1:
    ]:

        correlation = (
            correlation_matrix.loc[
                feature_a,
                feature_b,
            ]
        )

        if (
            pd.notna(correlation)
            and abs(correlation) >= 0.85
        ):
            strong_pairs.append(
                (
                    feature_a,
                    feature_b,
                    correlation,
                )
            )

print(
    "\nFeature pairs with absolute "
    "Spearman correlation >= 0.85:"
)

if strong_pairs:

    for feature_a, feature_b, value in (
        strong_pairs
    ):
        print(
            f"- {feature_a} <-> {feature_b}: "
            f"{value:.3f}"
        )
else:
    print("None detected.")

print(
    "\nNOTE: Correlations are descriptive "
    "only, based on 9 sections."
)

print(
    "Repeated road-level values reduce "
    "the effective independent information."
)


# ============================================================
# 8. FEATURE VALUES BY HUMAN LABEL
# ============================================================

heading("FEATURE PATTERNS BY HUMAN LABEL")

for feature in FEATURE_COLUMNS:

    print("\n" + "-" * 75)
    print("FEATURE:", feature)
    print("-" * 75)

    summary = (
        df.groupby(
            "priority_label"
        )[feature]
        .agg(
            ["count", "min", "median", "max"]
        )
        .reindex(CLASS_ORDER)
    )

    print(
        summary.to_string(
            float_format=lambda x: f"{x:.3f}"
        )
    )

print(
    "\nIMPORTANT: These summaries use "
    "all 9 human labels for exploration."
)

print(
    "Do not select features using these "
    "summaries and then claim an unbiased "
    "cross-validation accuracy."
)


# ============================================================
# 9. IDENTICAL FEATURES, DIFFERENT LABELS
# ============================================================

heading("IDENTICAL INPUT FEATURE CHECK")

conflicting_groups = []

grouped = df.groupby(
    FEATURE_COLUMNS,
    dropna=False,
)

for _, group in grouped:

    if group["priority_label"].nunique() > 1:
        conflicting_groups.append(group)

if conflicting_groups:

    print(
        "\nWARNING: Identical numeric inputs "
        "have different human labels."
    )

    for group in conflicting_groups:

        print(
            group[
                [
                    "section_id",
                    "road_id",
                    "priority_label",
                ]
            ].to_string(
                index=False
            )
        )
else:
    print(
        "\nNo identical complete feature "
        "vectors with conflicting labels."
    )

print(
    "\nNOTE: Different feature vectors "
    "can still be difficult to separate "
    "with only 9 examples."
)


# ============================================================
# 10. SECTION-LEVEL EVIDENCE TABLE
# ============================================================

heading("SECTION-LEVEL DATA REVIEW")

review_columns = [
    "section_id",
    "road_id",
    "priority_label",
] + FEATURE_COLUMNS

print(
    df[review_columns].to_string(
        index=False
    )
)


# ============================================================
# 11. RESEARCH INTERPRETATION
# ============================================================

heading("FEATURE ANALYSIS INTERPRETATION")

print("\n1. DATASET SIZE")
print(
    "Only 9 labelled sections across "
    "6 road groups are available."
)

print("\n2. FEATURE COUNT")
print(
    "There are 9 numeric predictor "
    "features for 9 observations."
)

print(
    "This creates a substantial "
    "overfitting risk."
)

print("\n3. ROAD-LEVEL EVIDENCE")
print(
    "Traffic and nearby-location counts "
    "are road-level, not section-specific."
)

print("\n4. PLANNED WORK")
print(
    "Planned maintenance items are not "
    "verified road damage observations."
)

print("\n5. FORECAST BUDGET")
print(
    "Forecast maintenance budget is not "
    "actual repair cost or proof of "
    "budget sufficiency."
)

print("\n6. TARGET")
print(
    "Human labels represent provisional "
    "maintenance / inspection priority."
)

print("\n7. FEATURE SELECTION")
print(
    "Any feature selection informed by "
    "all labels must be evaluated on "
    "new independent data or inside "
    "the training portion of each "
    "cross-validation fold."
)

print("\n8. ACCURACY IMPROVEMENT")
print(
    "Try simpler feature sets and "
    "model settings in a controlled "
    "road-group-aware experiment."
)

print(
    "Do not claim improvement from "
    "training-set accuracy alone."
)

print("\n9. BETTER DATA")
print(
    "More independently human-labelled "
    "sections and observed damage "
    "features are needed for reliable "
    "generalization."
)

print("\nNO AUTOMATIC LABELS GENERATED.")
print("NO EXISTING DATA FILES MODIFIED.")
print("NO MODELS TRAINED OR MODIFIED.")

print("\nSTEP 30 COMPLETED.")
