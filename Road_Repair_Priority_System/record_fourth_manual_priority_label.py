
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 19 - RECORD FOURTH MANUAL PRIORITY LABEL
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotations_after_third_review.csv"
)

OUTPUT_FILE = Path(
    "outputs/priority_annotations_after_fourth_review.csv"
)

SECTION_ID = "B214_0_18460"

# ============================================================
# USER'S HUMAN ASSESSMENT - NEVER AUTO-GENERATED
# ============================================================

HUMAN_LABEL = "Medium"
HUMAN_CONFIDENCE = "Low"

# Preserve user's original wording
HUMAN_REASON = (
    "Have medium traffic rate, nearby hospitals and high cost."
)

# AI suggestion - separate from human target
AI_RECOMMENDATION = "Medium"
AI_CONFIDENCE = "Low"

ANNOTATION_TARGET = (
    "provisional_maintenance_inspection_priority"
)

# Evidence limitations / discrepancies
LIMITATIONS = (
    "Evidence review note: the current road-level dataset "
    "reports 0 hospitals, 14 schools and 2 police stations "
    "within 500 m for B214. Therefore the user's mention "
    "of nearby hospitals is not supported by these counts. "
    "The forecast maintenance budget is not a confirmed "
    "repair cost. Traffic and POI features are road-level, "
    "not section-specific. Planned crack sealing is not "
    "confirmed actual damage. Actual damage severity "
    "is unavailable. The human reason is preserved "
    "verbatim pending review."
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
        f"Output already exists: {OUTPUT_FILE}\n"
        "Existing annotations were NOT overwritten."
    )


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    dtype={"section_id": "string"}
)

print("=" * 65)
print("RECORD FOURTH MANUAL PRIORITY LABEL")
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
    raise ValueError(
        "Missing section IDs detected."
    )

if df["section_id"].duplicated().any():
    raise ValueError(
        "Duplicate section IDs detected."
    )


# ============================================================
# 4. CONVERT ANNOTATION COLUMNS TO TEXT
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
# 5. VERIFY PREVIOUS THREE HUMAN LABELS
# ============================================================

expected_previous_labels = {
    "B047_0_3680": "High",
    "B047_3680_7420": "High",
    "B174_0_9490": "Low",
}

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
            f"Unexpected previous label for {previous_id}: "
            f"{actual_label}"
        )


# Save complete previous rows for verification
previous_rows_before = (
    df.loc[
        df["section_id"].isin(
            expected_previous_labels.keys()
        )
    ]
    .copy()
    .set_index("section_id")
    .sort_index()
)


# ============================================================
# 6. FIND FOURTH SECTION
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
    and str(existing_label).strip()
):
    raise ValueError(
        "Fourth section already has a priority label. "
        "Existing annotation was NOT overwritten."
    )


# ============================================================
# 7. CHECK PREVIOUS LABEL COUNT
# ============================================================

labels_before = (
    df["priority_label"]
    .fillna("")
    .str.strip()
)

assigned_before = int(
    labels_before.ne("").sum()
)

if assigned_before != 3:
    raise ValueError(
        f"Expected 3 existing human labels, "
        f"found {assigned_before}."
    )


# ============================================================
# 8. RECORD FOURTH HUMAN ASSESSMENT
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
    "road-level nearby important locations; "
    "section forecast maintenance budget; "
    "planned pavement maintenance records"
)

df.loc[
    mask, "additional_observations"
] = LIMITATIONS

df.loc[
    mask, "annotation_target"
] = ANNOTATION_TARGET


# ============================================================
# 9. STORE AI SUGGESTION SEPARATELY
# ============================================================

df.loc[
    mask, "ai_recommendation"
] = AI_RECOMMENDATION

df.loc[
    mask, "ai_recommendation_confidence"
] = AI_CONFIDENCE


# ============================================================
# 10. VERIFY PREVIOUS ROWS ARE UNCHANGED
# ============================================================

previous_rows_after = (
    df.loc[
        df["section_id"].isin(
            expected_previous_labels.keys()
        )
    ]
    .copy()
    .set_index("section_id")
    .sort_index()
)

pd.testing.assert_frame_equal(
    previous_rows_before,
    previous_rows_after,
    check_dtype=True,
)


# ============================================================
# 11. VALIDATE FOURTH ANNOTATION
# ============================================================

labels_after = (
    df["priority_label"]
    .fillna("")
    .str.strip()
)

assigned_after = int(
    labels_after.ne("").sum()
)

if assigned_after != 4:
    raise ValueError(
        f"Expected 4 human labels, "
        f"found {assigned_after}."
    )

saved_label = df.loc[
    mask, "priority_label"
].iloc[0]

saved_confidence = df.loc[
    mask, "annotation_confidence"
].iloc[0]

saved_reason = df.loc[
    mask, "annotation_reason"
].iloc[0]

if saved_label != HUMAN_LABEL:
    raise ValueError(
        "Fourth human label validation failed."
    )

if saved_confidence != HUMAN_CONFIDENCE:
    raise ValueError(
        "Fourth confidence validation failed."
    )

if saved_reason != HUMAN_REASON:
    raise ValueError(
        "Fourth human reason validation failed."
    )


# ============================================================
# 12. SAVE AS A NEW FILE
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
print("FOURTH MANUAL ANNOTATION SAVED SUCCESSFULLY")
print("=" * 65)

print("\nFourth section:", SECTION_ID)
print("Human priority:", HUMAN_LABEL)
print("Human confidence:", HUMAN_CONFIDENCE)
print("Human reason:", HUMAN_REASON)

print("\nAI recommendation:", AI_RECOMMENDATION)
print("AI confidence:", AI_CONFIDENCE)

print("\nPREVIOUS ANNOTATIONS:")
print("- B047_0_3680: High (preserved)")
print("- B047_3680_7420: High (preserved)")
print("- B174_0_9490: Low (preserved)")
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
print("- No formula-based labels were generated.")
print("- Previous human annotations were preserved.")
print("- AI suggestions are separate from human labels.")
print("- Evidence discrepancies were recorded.")
print("- Existing files and ML models were not modified.")

print("\nDONE!")
