
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 17 - RECORD SECOND MANUAL PRIORITY LABEL
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotations_in_progress.csv"
)

OUTPUT_FILE = Path(
    "outputs/priority_annotations_after_second_review.csv"
)

SECTION_ID = "B047_3680_7420"

# User's independent human assessment
HUMAN_LABEL = "High"
HUMAN_CONFIDENCE = "Medium"

HUMAN_REASON = (
    "High traffic and have some planned maintenance."
)

# AI recommendation - stored separately
AI_RECOMMENDATION = "High"
AI_CONFIDENCE = "Low"

LIMITATIONS = (
    "Traffic and nearby important-location features "
    "are road-level, not specific to this section. "
    "Planned maintenance is not confirmed damage. "
    "Actual damage severity is unavailable. "
    "The assessment is provisional."
)


# ============================================================
# 1. CHECK INPUT AND OUTPUT FILES
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"Output already exists: {OUTPUT_FILE}\n"
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
print("RECORD SECOND MANUAL PRIORITY LABEL")
print("=" * 65)

print("\nInput sections:", len(df))


# ============================================================
# 3. VALIDATE REQUIRED COLUMNS
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
        f"Missing columns: {missing}"
    )

if len(df) != 9:
    raise ValueError(
        f"Expected 9 sections, found {len(df)}."
    )

if df["section_id"].duplicated().any():
    raise ValueError(
        "Duplicate section IDs detected."
    )


# ============================================================
# 4. FIX ANNOTATION COLUMN DATA TYPES
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
# 5. VERIFY FIRST HUMAN LABEL IS PRESERVED
# ============================================================

first_mask = (
    df["section_id"] == "B047_0_3680"
)

if first_mask.sum() != 1:
    raise ValueError(
        "First annotated section was not found."
    )

first_label_before = df.loc[
    first_mask, "priority_label"
].iloc[0]

first_reason_before = df.loc[
    first_mask, "annotation_reason"
].iloc[0]

if first_label_before != "High":
    raise ValueError(
        "First section's High label is missing "
        "or has changed."
    )


# ============================================================
# 6. FIND SECOND SECTION
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
        "Second section already has a label. "
        "No existing annotation was overwritten."
    )


# ============================================================
# 7. RECORD USER'S SECOND ASSESSMENT
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
    "section-level planned pavement maintenance records; "
    "section forecast budget; "
    "road-level nearby important locations"
)

df.loc[
    mask, "additional_observations"
] = LIMITATIONS

df.loc[
    mask, "annotation_target"
] = "provisional_maintenance_inspection_priority"


# ============================================================
# 8. RECORD AI RECOMMENDATION SEPARATELY
# ============================================================

df.loc[
    mask, "ai_recommendation"
] = AI_RECOMMENDATION

df.loc[
    mask, "ai_recommendation_confidence"
] = AI_CONFIDENCE


# ============================================================
# 9. VALIDATE BOTH LABELS
# ============================================================

first_label_after = df.loc[
    first_mask, "priority_label"
].iloc[0]

first_reason_after = df.loc[
    first_mask, "annotation_reason"
].iloc[0]

if first_label_after != first_label_before:
    raise ValueError(
        "First label changed unexpectedly."
    )

if first_reason_after != first_reason_before:
    raise ValueError(
        "First annotation reason changed unexpectedly."
    )

labels = (
    df["priority_label"]
    .fillna("")
    .str.strip()
)

assigned_count = int(
    labels.ne("").sum()
)

if assigned_count != 2:
    raise ValueError(
        f"Expected exactly 2 labels, "
        f"found {assigned_count}."
    )

if df.loc[mask, "priority_label"].iloc[0] != "High":
    raise ValueError(
        "Second human label was not saved correctly."
    )


# ============================================================
# 10. SAVE AS A NEW FILE
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
# 11. PRINT RESULTS
# ============================================================

print("\n" + "=" * 65)
print("SECOND MANUAL ANNOTATION SAVED SUCCESSFULLY")
print("=" * 65)

print("\nSecond section:", SECTION_ID)
print("Human label:", HUMAN_LABEL)
print("Human confidence:", HUMAN_CONFIDENCE)
print("Human reason:", HUMAN_REASON)

print("\nAI recommendation:", AI_RECOMMENDATION)
print("AI confidence:", AI_CONFIDENCE)

print("\nFIRST LABEL CHECK:")
print("Section: B047_0_3680")
print("Preserved label:", first_label_after)
print("Reason preserved: Yes")

print("\nANNOTATION PROGRESS:")
print("Total sections:", len(df))
print("Assigned labels:", assigned_count)
print("Unlabelled sections:", len(df) - assigned_count)

print("\nALL ASSIGNED LABELS:")

print(
    df.loc[
        labels.ne(""),
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
print("- Both labels come from human assessments.")
print("- No formula-based priority labels were generated.")
print("- AI recommendations are stored separately.")
print("- Previous annotation file was not overwritten.")
print("- Existing trained ML models were not modified.")

print("\nDONE!")
