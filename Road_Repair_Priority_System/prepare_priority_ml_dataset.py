
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 28 - PREPARE EXPERIMENTAL SUPERVISED ML DATASET
#
# NO AUTOMATIC LABEL GENERATION
# NO MODEL TRAINING
# NO EXISTING FILE OVERWRITE
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotations_all_confidence_completed.csv"
)

OUTPUT_FILE = Path(
    "outputs/priority_ml_dataset_experimental.csv"
)

TARGET_COLUMN = "priority_label"

# Explicit feature whitelist.
# Do NOT automatically select every numeric column.

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

VALID_LABELS = {"High", "Medium", "Low"}

EXPECTED_TARGET = (
    "provisional_maintenance_inspection_priority"
)


# ============================================================
# 1. CHECK FILES
# ============================================================

if not INPUT_FILE.is_file():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"Output file already exists: {OUTPUT_FILE}\n"
        "Existing output was NOT overwritten."
    )


# ============================================================
# 2. READ HUMAN-ANNOTATED DATA
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    dtype={"section_id": "string"}
)

print("=" * 65)
print("STEP 28 - PREPARE EXPERIMENTAL ML DATASET")
print("=" * 65)

print("\nInput file:", INPUT_FILE)
print("Input rows:", len(df))


# ============================================================
# 3. VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = [
    "section_id",
    "road_id",
    TARGET_COLUMN,
    "annotation_target",
] + FEATURE_COLUMNS

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
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
    raise ValueError("Missing section IDs found.")

if df["section_id"].duplicated().any():
    raise ValueError("Duplicate section IDs found.")

if set(df["section_id"]) != set(EXPECTED_LABELS):
    raise ValueError(
        "Unexpected section IDs detected."
    )


# ============================================================
# 4. VERIFY EXISTING HUMAN LABELS
# ============================================================

df[TARGET_COLUMN] = (
    df[TARGET_COLUMN]
    .astype("string")
    .str.strip()
)

if not df[TARGET_COLUMN].isin(VALID_LABELS).all():
    raise ValueError(
        "Invalid or missing human labels detected."
    )

for section_id, expected_label in EXPECTED_LABELS.items():

    actual_label = df.loc[
        df["section_id"] == section_id,
        TARGET_COLUMN,
    ].iloc[0]

    if actual_label != expected_label:
        raise ValueError(
            f"Human label mismatch for {section_id}."
        )

targets = (
    df["annotation_target"]
    .astype("string")
    .str.strip()
)

if not targets.eq(
    EXPECTED_TARGET
).fillna(False).all():
    raise ValueError(
        "Unexpected annotation target detected."
    )

print("\nHuman labels: VALID")


# ============================================================
# 5. CHECK ROAD GROUPS
# ============================================================

df["road_id"] = (
    df["road_id"]
    .astype("string")
    .str.strip()
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
        "Road IDs do not match section IDs."
    )

road_count = df["road_id"].nunique()

if road_count != 6:
    raise ValueError(
        f"Expected 6 road groups, found {road_count}."
    )

print("Independent road groups:", road_count)


# ============================================================
# 6. SELECT ONLY APPROVED COLUMNS
# ============================================================

# section_id and road_id are retained for tracking
# and future grouped evaluation.
#
# They are NOT predictor features.

output_columns = [
    "section_id",
    "road_id",
] + FEATURE_COLUMNS + [
    TARGET_COLUMN
]

ml_df = df[output_columns].copy()


# ============================================================
# 7. CHECK FEATURE DATA TYPES
# ============================================================

for column in FEATURE_COLUMNS:

    ml_df[column] = pd.to_numeric(
        ml_df[column],
        errors="raise"
    )

missing_feature_values = (
    ml_df[FEATURE_COLUMNS]
    .isna()
    .sum()
)

if missing_feature_values.sum() > 0:
    raise ValueError(
        "Missing feature values detected:\n"
        + missing_feature_values.to_string()
    )

print("\nSelected numeric features:", len(FEATURE_COLUMNS))
print("Missing feature values: 0")


# ============================================================
# 8. CHECK FOR PROHIBITED PREDICTOR COLUMNS
# ============================================================

prohibited_columns = {
    "ai_recommendation",
    "ai_recommendation_confidence",
    "annotation_reason",
    "annotation_confidence",
    "annotation_target",
    "annotator_id",
    "annotation_date",
    "evidence_reviewed",
    "additional_observations",
    "damage_severity_status",
}

unexpected_columns = (
    prohibited_columns
    & set(ml_df.columns)
)

if unexpected_columns:
    raise ValueError(
        "Prohibited columns detected: "
        f"{sorted(unexpected_columns)}"
    )

if TARGET_COLUMN in FEATURE_COLUMNS:
    raise ValueError(
        "Target column included in predictors."
    )

if (
    "road_id" in FEATURE_COLUMNS
    or "section_id" in FEATURE_COLUMNS
):
    raise ValueError(
        "Identifier included in predictors."
    )

print("AI / annotation metadata excluded: YES")
print("Identifiers excluded from predictors: YES")


# ============================================================
# 9. VERIFY TARGET LABELS WERE PRESERVED
# ============================================================

original_labels = (
    df.set_index("section_id")[TARGET_COLUMN]
    .sort_index()
)

prepared_labels = (
    ml_df.set_index("section_id")[TARGET_COLUMN]
    .sort_index()
)

pd.testing.assert_series_equal(
    original_labels,
    prepared_labels,
    check_dtype=True,
    check_exact=True,
)

print("Human labels unchanged: YES")


# ============================================================
# 10. SAVE NEW FILE WITHOUT OVERWRITING
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with OUTPUT_FILE.open(
    mode="x",
    encoding="utf-8-sig",
    newline="",
) as output_handle:

    ml_df.to_csv(
        output_handle,
        index=False,
    )


# ============================================================
# 11. PRINT SUMMARY
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENTAL ML DATASET SAVED")
print("=" * 65)

print("\nOutput file:", OUTPUT_FILE)
print("Sections:", len(ml_df))
print("Road groups:", road_count)
print("Numeric predictor features:", len(FEATURE_COLUMNS))

print("\nFEATURES:")

for column in FEATURE_COLUMNS:
    print("-", column)

print("\nHUMAN LABEL DISTRIBUTION:")

print(
    ml_df[TARGET_COLUMN]
    .value_counts()
    .reindex(
        ["High", "Medium", "Low"],
        fill_value=0
    )
    .to_string()
)

print("\nDATASET PREVIEW:")

print(
    ml_df[
        [
            "section_id",
            "road_id",
            TARGET_COLUMN,
        ]
    ].to_string(index=False)
)

print("\nIMPORTANT LIMITATIONS:")
print("- This is an experimental dataset only.")
print("- Human labels are provisional.")
print("- Only 9 sections across 6 roads.")
print("- Traffic and POI features are road-level.")
print("- Forecast budget is not actual repair cost.")
print("- Planned work is not verified damage.")
print("- No actual damage severity is available.")
print("- Random section-wise splitting is unsafe.")
print("- Reliable ML accuracy cannot yet be claimed.")

print("\nNO AUTOMATIC LABELS GENERATED.")
print("NO EXISTING FILES OVERWRITTEN.")
print("NO MODELS TRAINED OR MODIFIED.")

print("\nDONE!")
