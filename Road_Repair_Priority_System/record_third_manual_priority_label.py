
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 18 - RECORD THIRD INDEPENDENT HUMAN LABEL
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotations_after_second_review.csv"
)

OUTPUT_FILE = Path(
    "outputs/priority_annotations_after_third_review.csv"
)

SECTION_ID = "B174_0_9490"

# User's independent assessment
HUMAN_LABEL = "Low"
HUMAN_CONFIDENCE = "Low"

# Preserve user's original reasoning
HUMAN_REASON = (
    "Low traffic rate, low planned maintenance and high cost."
)

# AI suggestion is NOT the human label
AI_RECOMMENDATION = "Medium"
AI_CONFIDENCE = "Low"

LIMITATIONS = (
    "Traffic is a road-level observation, not section-specific "
    "AADT. Planned maintenance is not confirmed damage. "
    "The forecast maintenance budget is not verified repair "
    "cost and does not establish cost suitability. "
    "Actual road damage severity is unavailable. "
    "This is a provisional human assessment."
)

ANNOTATION_TARGET = (
    "provisional_maintenance_inspection_priority"
)


# ============================================================
# 1. FILE SAFETY CHECKS
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"Output file already exists: {OUTPUT_FILE}\n"
        "Existing annotation work was NOT overwritten."
    )


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    dtype={"section_id": "string"}
)

print("=" * 65)
print("RECORD THIRD MANUAL PRIORITY LABEL")
print("=" * 65)

print("\nInput sections:", len(df))


# ============================================================
# 3. VALIDATE DATA STRUCTURE
# ============================================================

required_columns = [
    "section_id",
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
    "evidence_reviewed",
    "additional_observations",
    "annotation_target",
    "ai_recommendation",
    "ai_recommendation_confidence",
]

missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

if len(df) != 9:
    raise ValueError(
        f"Expected 9 sections, found {len(df)}."
    )

if df["section_id"].isna().any():
    raise ValueError(
        "Some section IDs are missing."
    )

if df["section_id"].duplicated().any():
    raise ValueError(
        "Duplicate section IDs detected."
    )


# ============================================================
# 4. FIX TEXT COLUMN DATA TYPES
# ============================================================

text_columns = [
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
    "evidence_reviewed",
    "additional_observations",
    "annotation_target",
    "ai_recommendation",
    "ai_recommendation_confidence",
]

for column in text_columns:
    df[column] = df[column].astype("string")


# ============================================================
# 5. CHECK PREVIOUS HUMAN ANNOTATIONS
# ============================================================

expected_previous_labels = {
    "B047_0_3680": "High",
    "B047_3680_7420": "High",
}

previous_masks = {}

for previous_id, expected_label in (
    expected_previous_labels.items()
):
    previous_mask = (
        df["section_id"] == previous_id
    )

    if previous_mask.sum() != 1:
        raise ValueError(
            f"Previous section missing: {previous_id}"
        )

    actual_label = df.loc[
        previous_mask, "priority_label"
    ].iloc[0]

    if actual_label != expected_label:
        raise ValueError(
            f"Previous label changed for {previous_id}."
        )

    previous_masks[previous_id] = previous_mask


# Preserve complete previous rows for later validation
previous_rows_before = (
    df.loc[
        df["section_id"].isin(
            expected_previous_labels.keys()
        )
    ]
    .copy()
    .set_index("section_id")
)


# ============================================================
# 6. FIND THIRD SECTION
# ============================================================

mask = df["section_id"] == SECTION_ID

if mask.sum() != 1:
    raise ValueError(
        f"Expected exactly one {SECTION_ID}, "
        f"found {mask.sum()}."
    )

existing_label = df.loc[
    mask, "priority_label"
].iloc[0]

if (
    pd.notna(existing_label)
    and str(existing_label).strip() != ""
):
    raise ValueError(
        "Third section already has a label. "
        "Existing annotation was NOT overwritten."
    )


# ============================================================
# 7. VERIFY ONLY TWO LABELS ALREADY EXIST
# ============================================================

labels_before = (
    df["priority_label"]
    .fillna("")
    .str.strip()
)

assigned_before = int(
    labels_before.ne("").sum()
)

if assigned_before != 2:
    raise ValueError(
        "Expected exactly 2 existing human labels, "
        f"found {assigned_before}."
    )


# ============================================================
# 8. RECORD THIRD HUMAN ASSESSMENT
# ============================================================

df.loc[
    mask, "priority_label"
] = HUMAN_LABEL

df.loc[
    mask, "annotation_confidence"
] = HUMAN_CONFIDENCE

df.loc[
    mask, "annotation_reason"
] = HUMAN_REASON

df.loc[
    mask, "evidence_reviewed"
] = (
    "Road-level traffic observations; "
    "section forecast maintenance budget; "
    "planned pavement maintenance records; "
    "road-level nearby important locations"
)

df.loc[
    mask, "additional_observations"
] = LIMITATIONS

df.loc[
    mask, "annotation_target"
] = ANNOTATION_TARGET


# ============================================================
# 9. RECORD AI RECOMMENDATION SEPARATELY
# ============================================================

df.loc[
    mask, "ai_recommendation"
] = AI_RECOMMENDATION

df.loc[
    mask, "ai_recommendation_confidence"
] = AI_CONFIDENCE


# ============================================================
# 10. VERIFY PREVIOUS ROWS WERE PRESERVED
# ============================================================

previous_rows_after = (
    df.loc[
        df["section_id"].isin(
            expected_previous_labels.keys()
        )
    ]
    .copy()
    .set_index("section_id")
)

pd.testing.assert_frame_equal(
    previous_rows_before.sort_index(),
    previous_rows_after.sort_index(),
    check_dtype=True,
)


# ============================================================
# 11. VALIDATE THIRD ANNOTATION
# ============================================================

labels_after = (
    df["priority_label"]
    .fillna("")
    .str.strip()
)

assigned_after = int(
    labels_after.ne("").sum()
)

if assigned_after != 3:
    raise ValueError(
        f"Expected 3 assigned labels, "
        f"found {assigned_after}."
    )

saved_label = df.loc[
    mask, "priority_label"
].iloc[0]

saved_confidence = df.loc[
    mask, "annotation_confidence"
].iloc[0]

if saved_label != "Low":
    raise ValueError(
        "Third human label validation failed."
    )

if saved_confidence != "Low":
    raise ValueError(
        "Third human confidence validation failed."
    )


# ============================================================
# 12. SAVE NEW FILE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 13. PRINT RESULTS
# ============================================================

print("\n" + "=" * 65)
print("THIRD MANUAL ANNOTATION SAVED SUCCESSFULLY")
print("=" * 65)

print("\nThird section:", SECTION_ID)
print("Human priority:", HUMAN_LABEL)
print("Human confidence:", HUMAN_CONFIDENCE)
print("Human reason:", HUMAN_REASON)

print("\nAI recommendation:", AI_RECOMMENDATION)
print("AI confidence:", AI_CONFIDENCE)

print("\nPREVIOUS ANNOTATIONS:")
print("- B047_0_3680: High (preserved)")
print("- B047_3680_7420: High (preserved)")
print("- Previous rows unchanged: Yes")

print("\nANNOTATION PROGRESS:")
print("Total sections:", len(df))
print("Assigned labels:", assigned_after)
print("Unlabelled sections:", len(df) - assigned_after)

print("\nALL ASSIGNED HUMAN LABELS:")

print(
    df.loc[
        labels_after.ne(""),
        [
            "section_id",
            "priority_label",
            "annotation_confidence",
            "annotation_reason",
        ]
    ].to_string(index=False)
)

print("\nOutput file:", OUTPUT_FILE)

print("\nIMPORTANT:")
print("- No automatic priority label generation.")
print("- Human assessments were preserved.")
print("- AI recommendations stored separately.")
print("- Original files were not overwritten.")
print("- Existing trained models were not modified.")

print("\nDONE!")
