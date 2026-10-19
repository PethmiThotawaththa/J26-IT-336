
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 25 - VALIDATE COMPLETED MANUAL ANNOTATIONS
# READ ONLY - NO MODEL TRAINING
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotations_after_ninth_review.csv"
)

EXPECTED_SECTION_IDS = {
    "B047_0_3680",
    "B047_3680_7420",
    "B174_0_9490",
    "B214_0_18460",
    "B214_18460_28520",
    "B240_0_2550",
    "B240_2550_13100",
    "B263_0_5555",
    "B435_0_7700",
}

VALID_LABELS = {"High", "Medium", "Low"}

EXPECTED_TARGET = (
    "provisional_maintenance_inspection_priority"
)


# ============================================================
# 1. LOAD DATA
# ============================================================

if not INPUT_FILE.is_file():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

df = pd.read_csv(
    INPUT_FILE,
    dtype={"section_id": "string"}
)

print("=" * 65)
print("VALIDATE COMPLETED MANUAL PRIORITY ANNOTATIONS")
print("=" * 65)

print("\nInput file:", INPUT_FILE)
print("Total rows:", len(df))
print("Total columns:", len(df.columns))


# ============================================================
# 2. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "section_id",
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
    "annotation_target",
    "ai_recommendation",
    "ai_recommendation_confidence",
    "additional_observations",
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("\nRequired columns: PASS")


# ============================================================
# 3. CHECK SECTION IDENTITIES
# ============================================================

if len(df) != 9:
    raise ValueError(
        f"Expected 9 rows, found {len(df)}."
    )

if df["section_id"].isna().any():
    raise ValueError("Missing section IDs found.")

if df["section_id"].duplicated().any():
    raise ValueError("Duplicate section IDs found.")

actual_ids = set(df["section_id"].tolist())

if actual_ids != EXPECTED_SECTION_IDS:
    missing_ids = EXPECTED_SECTION_IDS - actual_ids
    extra_ids = actual_ids - EXPECTED_SECTION_IDS

    raise ValueError(
        f"Section ID mismatch.\n"
        f"Missing: {sorted(missing_ids)}\n"
        f"Unexpected: {sorted(extra_ids)}"
    )

print("Section IDs: PASS")
print("Duplicate section IDs: 0")


# ============================================================
# 4. CHECK HUMAN PRIORITY LABELS
# ============================================================

labels = (
    df["priority_label"]
    .astype("string")
    .str.strip()
)

if labels.isna().any():
    raise ValueError("Missing human priority labels.")

if not labels.isin(VALID_LABELS).all():
    invalid = labels[
        ~labels.isin(VALID_LABELS)
    ].tolist()

    raise ValueError(
        f"Invalid human priority labels: {invalid}"
    )

print("\nHuman priority labels: PASS")

print("\nLABEL DISTRIBUTION:")

print(
    labels.value_counts()
    .reindex(
        ["High", "Medium", "Low"],
        fill_value=0
    )
    .to_string()
)


# ============================================================
# 5. CHECK HUMAN ANNOTATION REASONS
# ============================================================

reasons = (
    df["annotation_reason"]
    .astype("string")
    .fillna("")
    .str.strip()
)

missing_reason_count = int(
    reasons.eq("").sum()
)

print("\nHuman reasons missing:", missing_reason_count)

if missing_reason_count > 0:
    raise ValueError(
        "Some human annotation reasons are missing."
    )


# ============================================================
# 6. CHECK HUMAN CONFIDENCE
# ============================================================

confidence = (
    df["annotation_confidence"]
    .astype("string")
    .str.strip()
)

valid_confidence = {"High", "Medium", "Low"}

invalid_confidence = (
    confidence.notna()
    & ~confidence.isin(valid_confidence)
)

if invalid_confidence.any():
    raise ValueError(
        "Invalid human confidence values found."
    )

missing_confidence = df.loc[
    confidence.isna() | confidence.eq("").fillna(False),
    "section_id",
].tolist()

print("\nHUMAN CONFIDENCE CHECK:")

print(
    "Missing confidence values:",
    len(missing_confidence)
)

if missing_confidence:
    print(
        "Sections with missing confidence:",
        missing_confidence
    )

    print(
        "NOTE: Missing confidence is not "
        "automatically filled."
    )


# ============================================================
# 7. CHECK ANNOTATION TARGET
# ============================================================

targets = (
    df["annotation_target"]
    .astype("string")
    .str.strip()
)

if not targets.eq(EXPECTED_TARGET).fillna(False).all():
    raise ValueError(
        "Annotation target mismatch detected."
    )

print("\nAnnotation target: PASS")
print("Target:", EXPECTED_TARGET)


# ============================================================
# 8. CHECK AI RECOMMENDATIONS
# ============================================================

ai_labels = (
    df["ai_recommendation"]
    .astype("string")
    .str.strip()
)

ai_confidence = (
    df["ai_recommendation_confidence"]
    .astype("string")
    .str.strip()
)

if not ai_labels.isin(VALID_LABELS).all():
    raise ValueError(
        "Missing or invalid AI recommendations found."
    )

if not ai_confidence.isin(valid_confidence).all():
    raise ValueError(
        "Missing or invalid AI confidence values found."
    )

print("\nAI recommendation columns: PASS")
print("AI recommendations stored separately: Yes")

agreement_count = int(
    labels.eq(ai_labels).sum()
)

print(
    "Human-AI label agreement:",
    f"{agreement_count}/9"
)

print(
    "NOTE: Agreement is descriptive only. "
    "It is NOT model accuracy or validation."
)


# ============================================================
# 9. DISPLAY COMPLETED HUMAN ANNOTATIONS
# ============================================================

print("\n" + "=" * 65)
print("COMPLETED HUMAN ANNOTATION DATASET")
print("=" * 65)

print(
    df[
        [
            "section_id",
            "priority_label",
            "annotation_confidence",
            "annotation_reason",
        ]
    ].to_string(index=False)
)


# ============================================================
# 10. FINAL VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 65)
print("VALIDATION COMPLETED")
print("=" * 65)

print("\nTotal sections:", len(df))
print("Valid human labels:", len(labels))
print("Unlabelled sections:", 0)

print(
    "Missing human confidence:",
    len(missing_confidence)
)

print("\nIMPORTANT:")
print("- No labels were generated or changed.")
print("- No CSV files were modified.")
print("- No ML models were modified.")
print("- AI recommendations must NOT be used")
print("  as model training features.")
print("- These are provisional human judgments.")
print("- Actual damage severity remains unavailable.")
print("- Nine sections are insufficient for")
print("  reliable supervised ML generalization.")

print("\nDONE!")
