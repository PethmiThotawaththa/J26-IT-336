
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 24 - RECORD NINTH MANUAL PRIORITY LABEL
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotations_after_eighth_review.csv"
)

OUTPUT_FILE = Path(
    "outputs/priority_annotations_after_ninth_review.csv"
)

SECTION_ID = "B435_0_7700"


# ============================================================
# USER'S HUMAN ASSESSMENT
# NO AUTOMATIC LABEL GENERATION
# ============================================================

HUMAN_LABEL = "Medium"
HUMAN_CONFIDENCE = "Medium"

# Preserve user's original reason exactly
HUMAN_REASON = (
    "Have medium Traffic rate ,high budget and "
    "planned three pavement works."
)

# AI recommendation stored separately
AI_RECOMMENDATION = "Medium"
AI_CONFIDENCE = "Low"

ANNOTATION_TARGET = (
    "provisional_maintenance_inspection_priority"
)

EVIDENCE_REVIEWED = (
    "Road-level traffic observations; "
    "road-level nearby important locations; "
    "section-level planned pavement maintenance; "
    "section forecast maintenance budget"
)

LIMITATIONS = (
    "The user's original human reason is preserved. "
    "B435 has planned crack sealing, pothole patching "
    "and section overlay. These are three planned "
    "pavement maintenance work types, not three "
    "independently verified road damage observations. "
    "The section forecast maintenance budget is "
    "LKR 13,318,927.26, which is not a confirmed "
    "repair cost or evidence of budget sufficiency. "
    "Traffic observations and nearby important "
    "location counts are road-level, not "
    "section-specific. Traffic observations "
    "are not AADT. Actual road damage severity "
    "is unavailable. This assessment is a "
    "provisional maintenance or inspection priority. "
    "The AI recommendation was visible during "
    "human annotation, so the annotation is not "
    "fully AI-blinded."
)


# ============================================================
# 1. CHECK INPUT AND OUTPUT FILES
# ============================================================

if not INPUT_FILE.is_file():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"Output already exists: {OUTPUT_FILE}\n"
        "Existing annotation data was NOT overwritten."
    )


# ============================================================
# 2. LOAD INPUT CSV
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    dtype={"section_id": "string"}
)

print("=" * 65)
print("RECORD NINTH MANUAL PRIORITY LABEL")
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
# 4. CONVERT ANNOTATION COLUMNS TO STRING
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
# 5. VERIFY PREVIOUS EIGHT HUMAN LABELS
# ============================================================

expected_previous_labels = {
    "B047_0_3680": "High",
    "B047_3680_7420": "High",
    "B174_0_9490": "Low",
    "B214_0_18460": "Medium",
    "B214_18460_28520": "Medium",
    "B240_0_2550": "High",
    "B240_2550_13100": "Low",
    "B263_0_5555": "High",
}

for previous_id, expected_label in (
    expected_previous_labels.items()
):
    previous_mask = (
        df["section_id"] == previous_id
    )

    if int(previous_mask.sum()) != 1:
        raise ValueError(
            f"Previous section missing or duplicated: "
            f"{previous_id}"
        )

    actual_label = df.loc[
        previous_mask, "priority_label"
    ].iloc[0]

    if (
        pd.isna(actual_label)
        or actual_label != expected_label
    ):
        raise ValueError(
            f"Previous label mismatch for {previous_id}. "
            f"Expected {expected_label}, "
            f"found {actual_label}."
        )


# ============================================================
# 6. PRESERVE ALL PREVIOUS ANNOTATED ROWS
# ============================================================

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
# 7. LOCATE NINTH SECTION
# ============================================================

mask = df["section_id"] == SECTION_ID

if int(mask.sum()) != 1:
    raise ValueError(
        f"Expected exactly one {SECTION_ID}, "
        f"found {int(mask.sum())}."
    )

existing_label = df.loc[
    mask, "priority_label"
].iloc[0]

if (
    pd.notna(existing_label)
    and str(existing_label).strip()
):
    raise ValueError(
        "Ninth section already has a human label. "
        "Existing annotation was NOT overwritten."
    )


# ============================================================
# 8. VERIFY EXACTLY EIGHT LABELS EXIST
# ============================================================

labels_before = (
    df["priority_label"]
    .fillna("")
    .str.strip()
)

assigned_before = int(
    labels_before.ne("").sum()
)

if assigned_before != 8:
    raise ValueError(
        f"Expected 8 existing human labels, "
        f"found {assigned_before}."
    )


# ============================================================
# 9. RECORD USER'S NINTH HUMAN ASSESSMENT
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
] = EVIDENCE_REVIEWED

df.loc[
    mask, "additional_observations"
] = LIMITATIONS

df.loc[
    mask, "annotation_target"
] = ANNOTATION_TARGET


# ============================================================
# 10. RECORD AI SUGGESTION SEPARATELY
# ============================================================

df.loc[
    mask, "ai_recommendation"
] = AI_RECOMMENDATION

df.loc[
    mask, "ai_recommendation_confidence"
] = AI_CONFIDENCE


# ============================================================
# 11. VERIFY PREVIOUS ROWS ARE UNCHANGED
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
# 12. VALIDATE NINTH ANNOTATION
# ============================================================

labels_after = (
    df["priority_label"]
    .fillna("")
    .str.strip()
)

assigned_after = int(
    labels_after.ne("").sum()
)

if assigned_after != 9:
    raise ValueError(
        f"Expected 9 assigned labels, "
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

saved_ai_recommendation = df.loc[
    mask, "ai_recommendation"
].iloc[0]

saved_ai_confidence = df.loc[
    mask, "ai_recommendation_confidence"
].iloc[0]

if saved_label != HUMAN_LABEL:
    raise ValueError(
        "Ninth human priority validation failed."
    )

if saved_confidence != HUMAN_CONFIDENCE:
    raise ValueError(
        "Ninth human confidence validation failed."
    )

if saved_reason != HUMAN_REASON:
    raise ValueError(
        "Ninth human reason validation failed."
    )

if saved_ai_recommendation != AI_RECOMMENDATION:
    raise ValueError(
        "AI recommendation validation failed."
    )

if saved_ai_confidence != AI_CONFIDENCE:
    raise ValueError(
        "AI confidence validation failed."
    )


# ============================================================
# 13. SAVE AS NEW CSV
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
# 14. PRINT RESULTS
# ============================================================

print("\n" + "=" * 65)
print("NINTH MANUAL ANNOTATION SAVED SUCCESSFULLY")
print("=" * 65)

print("\nNinth section:", SECTION_ID)
print("Human priority:", HUMAN_LABEL)
print("Human confidence:", HUMAN_CONFIDENCE)
print("Human reason:", HUMAN_REASON)

print("\nAI recommendation:", AI_RECOMMENDATION)
print("AI confidence:", AI_CONFIDENCE)

print("\nPREVIOUS ANNOTATIONS:")

for previous_id, expected_label in (
    expected_previous_labels.items()
):
    print(
        f"- {previous_id}: "
        f"{expected_label} (preserved)"
    )

print("- Previous rows unchanged: Yes")

print("\nANNOTATION PROGRESS:")
print("Total sections:", len(df))
print("Assigned labels:", assigned_after)
print(
    "Unlabelled sections:",
    len(df) - assigned_after
)

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

print("\nLABEL DISTRIBUTION:")

print(
    df["priority_label"]
    .value_counts()
    .reindex(
        ["High", "Medium", "Low"],
        fill_value=0
    )
    .to_string()
)

print("\nOutput file:", OUTPUT_FILE)

print("\nIMPORTANT:")
print("- No automatic priority labels generated.")
print("- Previous eight human annotations preserved.")
print("- AI suggestion stored separately.")
print("- No existing input files overwritten.")
print("- Existing trained ML models not modified.")
print("- This dataset is provisional, not verified")
print("  road damage or repair urgency ground truth.")

print("\nDONE!")
