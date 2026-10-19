
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 26 - COMPLETE ONE MISSING HUMAN CONFIDENCE
#
# ONLY UPDATE:
# B047_0_3680 -> annotation_confidence = Medium
#
# NO AUTOMATIC LABEL GENERATION
# NO EXISTING FILE OVERWRITE
# NO ML MODEL MODIFICATION
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotations_after_ninth_review.csv"
)

OUTPUT_FILE = Path(
    "outputs/priority_annotations_all_confidence_completed.csv"
)

TARGET_SECTION = "B047_0_3680"
NEW_CONFIDENCE = "Medium"

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
        f"Output already exists: {OUTPUT_FILE}\n"
        "Existing output was NOT overwritten."
    )


# ============================================================
# 2. LOAD EXISTING ANNOTATIONS
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    dtype={"section_id": "string"}
)

print("=" * 65)
print("COMPLETE MISSING HUMAN ANNOTATION CONFIDENCE")
print("=" * 65)

print("\nInput file:", INPUT_FILE)
print("Total rows:", len(df))
print("Total columns:", len(df.columns))


# ============================================================
# 3. VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = [
    "section_id",
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
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


# ============================================================
# 4. VALIDATE ALL NINE SECTIONS
# ============================================================

if len(df) != 9:
    raise ValueError(
        f"Expected 9 sections, found {len(df)}."
    )

if df["section_id"].isna().any():
    raise ValueError("Missing section IDs found.")

if df["section_id"].duplicated().any():
    raise ValueError("Duplicate section IDs found.")

actual_section_ids = set(
    df["section_id"].tolist()
)

if actual_section_ids != set(EXPECTED_LABELS):
    raise ValueError(
        "Section IDs do not match expected "
        "nine annotated sections."
    )

print("\nSection validation: PASS")


# ============================================================
# 5. VALIDATE ALL HUMAN PRIORITY LABELS
# ============================================================

for section_id, expected_label in (
    EXPECTED_LABELS.items()
):
    actual_label = df.loc[
        df["section_id"] == section_id,
        "priority_label",
    ].iloc[0]

    if (
        pd.isna(actual_label)
        or str(actual_label).strip() != expected_label
    ):
        raise ValueError(
            f"Priority label mismatch for {section_id}. "
            f"Expected {expected_label}, "
            f"found {actual_label}."
        )

print("All nine human priority labels: PASS")


# ============================================================
# 6. VALIDATE HUMAN REASONS
# ============================================================

reasons = (
    df["annotation_reason"]
    .astype("string")
    .fillna("")
    .str.strip()
)

if reasons.eq("").any():
    raise ValueError(
        "One or more human reasons are missing."
    )

print("All nine human reasons: PASS")


# ============================================================
# 7. VALIDATE ANNOTATION TARGET
# ============================================================

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

print("Annotation target: PASS")


# ============================================================
# 8. VALIDATE EXISTING CONFIDENCE VALUES
# ============================================================

df["annotation_confidence"] = (
    df["annotation_confidence"].astype("string")
)

confidence = (
    df["annotation_confidence"].str.strip()
)

valid_confidence = {"High", "Medium", "Low"}

invalid_confidence = (
    confidence.notna()
    & ~confidence.isin(valid_confidence)
)

if invalid_confidence.any():
    raise ValueError(
        "Invalid existing confidence value detected."
    )

missing_confidence_mask = (
    confidence.isna()
    | confidence.eq("").fillna(False)
)

missing_confidence_sections = df.loc[
    missing_confidence_mask,
    "section_id",
].tolist()

if missing_confidence_sections != [TARGET_SECTION]:
    raise ValueError(
        "Expected exactly one missing confidence "
        f"for {TARGET_SECTION}, but found: "
        f"{missing_confidence_sections}"
    )

print(
    "Missing confidence before update:",
    missing_confidence_sections
)


# ============================================================
# 9. MAKE COMPLETE BACKUP IN MEMORY
# ============================================================

# This is a DataFrame copy, NOT a file overwrite.
# We use it to prove that every other cell is unchanged.

original_df = df.copy(deep=True)


# ============================================================
# 10. UPDATE ONLY THE REQUESTED CONFIDENCE
# ============================================================

target_mask = (
    df["section_id"] == TARGET_SECTION
)

if int(target_mask.sum()) != 1:
    raise ValueError(
        "Target section missing or duplicated."
    )

df.loc[
    target_mask,
    "annotation_confidence",
] = NEW_CONFIDENCE


# ============================================================
# 11. VERIFY EXACTLY ONE CELL CHANGED
# ============================================================

expected_df = original_df.copy(deep=True)

expected_df.loc[
    target_mask,
    "annotation_confidence",
] = NEW_CONFIDENCE

pd.testing.assert_frame_equal(
    df,
    expected_df,
    check_dtype=True,
    check_exact=True,
)

# Independently verify every column except confidence
# remains identical across all nine rows.

other_columns = [
    column
    for column in df.columns
    if column != "annotation_confidence"
]

pd.testing.assert_frame_equal(
    original_df[other_columns],
    df[other_columns],
    check_dtype=True,
    check_exact=True,
)

# Verify the other eight confidence values
# are also unchanged.

other_sections_mask = ~target_mask

pd.testing.assert_series_equal(
    original_df.loc[
        other_sections_mask,
        "annotation_confidence",
    ],
    df.loc[
        other_sections_mask,
        "annotation_confidence",
    ],
    check_dtype=True,
    check_exact=True,
)

print("\nData preservation checks: PASS")
print("All nine human labels preserved: YES")
print("All nine human reasons preserved: YES")
print("All AI recommendations preserved: YES")
print("All other cells preserved: YES")


# ============================================================
# 12. VERIFY ALL CONFIDENCE VALUES ARE COMPLETE
# ============================================================

updated_confidence = (
    df["annotation_confidence"]
    .astype("string")
    .str.strip()
)

if updated_confidence.isna().any():
    raise ValueError(
        "Missing confidence still exists."
    )

if not updated_confidence.isin(
    valid_confidence
).all():
    raise ValueError(
        "Invalid or blank confidence found."
    )

print("\nAll human confidence values: COMPLETE")


# ============================================================
# 13. SAVE NEW FILE SAFELY
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

# Exclusive creation prevents accidental overwrite,
# including if the file appears after the initial check.

with OUTPUT_FILE.open(
    mode="x",
    encoding="utf-8-sig",
    newline="",
) as output_handle:
    df.to_csv(
        output_handle,
        index=False,
    )


# ============================================================
# 14. VERIFY SAVED CSV
# ============================================================

saved_df = pd.read_csv(
    OUTPUT_FILE,
    dtype={"section_id": "string"}
)

if len(saved_df) != 9:
    raise ValueError(
        "Saved CSV does not contain nine sections."
    )

saved_confidence = saved_df.loc[
    saved_df["section_id"] == TARGET_SECTION,
    "annotation_confidence",
].iloc[0]

if saved_confidence != NEW_CONFIDENCE:
    raise ValueError(
        "Saved confidence does not match "
        "the user's assessment."
    )


# ============================================================
# 15. PRINT FINAL RESULTS
# ============================================================

print("\n" + "=" * 65)
print("HUMAN CONFIDENCE UPDATE SAVED SUCCESSFULLY")
print("=" * 65)

print("\nUpdated section:", TARGET_SECTION)
print("Updated field: annotation_confidence")
print("Previous value: Missing")
print("New value:", NEW_CONFIDENCE)

print("\nANNOTATION COMPLETENESS:")
print("Total sections:", len(df))
print("Human labels completed:", len(df))
print("Human confidence completed:", len(df))
print("Missing confidence:", 0)

print("\nFINAL HUMAN ANNOTATIONS:")

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

print("\nOutput file:", OUTPUT_FILE)

print("\nIMPORTANT:")
print("- Only one confidence value was updated.")
print("- No automatic priority labels generated.")
print("- All nine human labels preserved.")
print("- All nine human reasons preserved.")
print("- AI recommendation columns unchanged.")
print("- Original CSV was NOT overwritten.")
print("- Existing trained ML models NOT modified.")

print("\nDONE!")
