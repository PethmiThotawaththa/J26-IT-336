
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 16 - SAVE FIRST MANUAL PRIORITY LABEL (FIXED)
# ============================================================

INPUT_FILE = Path(
    "outputs/complete_priority_evidence_review.csv"
)

OUTPUT_FILE = Path(
    "outputs/priority_annotations_in_progress.csv"
)

SECTION_ID = "B047_0_3680"

# User's independent human assessment
HUMAN_LABEL = "High"

HUMAN_REASON = (
    "Nearby important locations and high traffic "
    "and suitable for budget."
)

# AI suggestion - stored separately, not used as label
AI_RECOMMENDATION = "Medium"
AI_CONFIDENCE = "Low"

LIMITATIONS = (
    "Traffic and nearby-location data are road-level, "
    "not section-specific. Forecast budget does not "
    "establish repair urgency or budget sufficiency. "
    "Actual damage severity is unavailable."
)


# ============================================================
# 1. CHECK FILES
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"Output already exists: {OUTPUT_FILE}\n"
        "Existing manual annotations were NOT overwritten."
    )


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    dtype={"section_id": "string"}
)

print("=" * 65)
print("RECORD FIRST MANUAL PRIORITY LABEL")
print("=" * 65)

print("\nInput rows:", len(df))


# ============================================================
# 3. VALIDATE REQUIRED COLUMNS
# ============================================================

text_columns = [
    "priority_label",
    "annotation_reason",
    "annotation_confidence",
    "evidence_reviewed",
    "additional_observations",
    "annotator_id",
    "annotation_date",
    "annotation_target",
]

missing = [
    column
    for column in text_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Missing annotation columns: {missing}"
    )

if df["section_id"].duplicated().any():
    raise ValueError(
        "Duplicate section IDs detected."
    )


# ============================================================
# 4. FIX PANDAS DATA TYPES
# ============================================================

# Empty CSV columns can be inferred as float64.
# Convert annotation columns to pandas StringDtype.

for column in text_columns:
    df[column] = df[column].astype("string")

df["ai_recommendation"] = pd.Series(
    pd.NA,
    index=df.index,
    dtype="string"
)

df["ai_recommendation_confidence"] = pd.Series(
    pd.NA,
    index=df.index,
    dtype="string"
)


# ============================================================
# 5. FIND SECTION
# ============================================================

mask = df["section_id"] == SECTION_ID

if mask.sum() != 1:
    raise ValueError(
        f"Expected one section {SECTION_ID}; "
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
        "Section already has a label. "
        "Existing annotation was not changed."
    )


# ============================================================
# 6. RECORD HUMAN ASSESSMENT
# ============================================================

df.loc[
    mask, "priority_label"
] = HUMAN_LABEL

df.loc[
    mask, "annotation_reason"
] = HUMAN_REASON

# User did not specify confidence.
# Do not invent a confidence value.
df.loc[
    mask, "annotation_confidence"
] = pd.NA

df.loc[
    mask, "evidence_reviewed"
] = (
    "Road-level traffic; nearby hospitals and schools; "
    "section forecast budget; planned pavement maintenance"
)

df.loc[
    mask, "additional_observations"
] = LIMITATIONS

df.loc[
    mask, "annotation_target"
] = "provisional_maintenance_inspection_priority"


# ============================================================
# 7. STORE AI RECOMMENDATION SEPARATELY
# ============================================================

df.loc[
    mask, "ai_recommendation"
] = AI_RECOMMENDATION

df.loc[
    mask, "ai_recommendation_confidence"
] = AI_CONFIDENCE


# ============================================================
# 8. VALIDATE
# ============================================================

if len(df) != 9:
    raise ValueError(
        f"Expected 9 sections, found {len(df)}."
    )

labels = (
    df["priority_label"]
    .fillna("")
    .str.strip()
)

assigned_count = int(
    labels.ne("").sum()
)

if assigned_count != 1:
    raise ValueError(
        "Expected exactly one assigned label, "
        f"found {assigned_count}."
    )


# ============================================================
# 9. SAVE NEW FILE
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
# 10. PRINT RESULT
# ============================================================

print("\n" + "=" * 65)
print("MANUAL ANNOTATION SAVED SUCCESSFULLY")
print("=" * 65)

print("\nSection:", SECTION_ID)
print("Human priority label:", HUMAN_LABEL)
print("Human reason:", HUMAN_REASON)

print("\nAI recommendation:", AI_RECOMMENDATION)
print("AI confidence:", AI_CONFIDENCE)

print("\nTotal sections:", len(df))
print("Assigned labels:", assigned_count)
print("Unlabelled sections:", len(df) - assigned_count)

print("\nOutput file:", OUTPUT_FILE)

print("\nIMPORTANT:")
print("- No rule-based label generation.")
print("- Human label and AI recommendation stored separately.")
print("- Existing trained models were not modified.")
print("- Original evidence review file was not overwritten.")

print("\nDONE!")
