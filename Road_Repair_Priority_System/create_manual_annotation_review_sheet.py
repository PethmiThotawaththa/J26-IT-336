
from pathlib import Path
import pandas as pd


# ============================================================
# STEP 13 - MANUAL ANNOTATION REVIEW SHEET
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotation_review_with_damage_work.csv"
)

OUTPUT_FILE = Path(
    "outputs/manual_priority_review_sheet.csv"
)


# ============================================================
# 1. CHECK FILES
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

# Never overwrite a review sheet containing manual work.
if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"Review sheet already exists: {OUTPUT_FILE}\n"
        "Existing annotations were NOT overwritten."
    )


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 65)
print("CREATING MANUAL PRIORITY REVIEW SHEET")
print("=" * 65)

print("\nInput rows:", len(df))
print("Input columns:", len(df.columns))


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "section_id",
    "road_id",
    "section_start_m",
    "section_end_m",
    "section_length_m",
    "traffic_mean_vehicles_per_hour",
    "section_forecast_budget_lkr",
    "section_forecast_budget_per_km_lkr",
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "planned_item_1_present",
    "planned_item_2_present",
    "planned_item_75_present",
    "planned_damage_work_descriptions",
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

if df["section_id"].duplicated().any():
    raise ValueError(
        "Duplicate section IDs detected."
    )


# ============================================================
# 4. SELECT EVIDENCE COLUMNS
# ============================================================

review_columns = [
    "section_id",
    "road_id",
    "road_name",
    "section_start_m",
    "section_end_m",
    "section_length_m",

    # Traffic evidence - road-level
    "traffic_mean_vehicles_per_hour",

    # Budget evidence - section-level
    "section_forecast_budget_lkr",
    "section_forecast_budget_per_km_lkr",
    "section_budget_work_item_count",

    # Nearby facilities - road-level
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "nearest_hospital_distance_m",

    # Planned pavement maintenance evidence
    "damage_related_work_item_count",
    "damage_related_forecast_budget_lkr",
    "planned_item_1_present",
    "planned_item_2_present",
    "planned_item_75_present",
    "planned_damage_work_descriptions",
]

available_columns = [
    col for col in review_columns
    if col in df.columns
]

review = df[available_columns].copy()


# ============================================================
# 5. ADD HUMAN-READABLE PLANNED WORK COLUMNS
# ============================================================

work_mapping = {
    "planned_item_1_present": "Patching potholes",
    "planned_item_2_present": "Crack sealing",
    "planned_item_75_present": "Section overlay",
}

for source_column, description in work_mapping.items():

    new_column = (
        source_column.replace("_present", "_description")
    )

    review[new_column] = df[source_column].apply(
        lambda value: description
        if pd.notna(value) and int(value) == 1
        else ""
    )


# ============================================================
# 6. ADD BLANK MANUAL ANNOTATION FIELDS
# ============================================================

# All manual decisions are intentionally blank.
# No formula, thresholds, or automatic priority rules.

review["priority_label"] = ""
review["annotation_confidence"] = ""
review["annotation_reason"] = ""
review["evidence_reviewed"] = ""
review["additional_observations"] = ""
review["annotator_id"] = ""
review["annotation_date"] = ""

review["annotation_target"] = (
    "provisional_maintenance_inspection_priority"
)

review["damage_severity_status"] = (
    "pending_component_1"
)


# ============================================================
# 7. SORT AND SAVE
# ============================================================

review = review.sort_values(
    [
        "road_id",
        "section_start_m",
        "section_end_m",
    ]
).reset_index(drop=True)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

review.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. PRINT RESULTS
# ============================================================

print("\n" + "=" * 65)
print("MANUAL PRIORITY REVIEW SHEET CREATED")
print("=" * 65)

print("\nOutput file:", OUTPUT_FILE)
print("Total sections:", len(review))
print("Total columns:", len(review.columns))

print("\nSECTION EVIDENCE SUMMARY:")

display_columns = [
    "section_id",
    "planned_damage_work_descriptions",
    "section_forecast_budget_lkr",
]

print(
    review[display_columns].to_string(
        index=False
    )
)

print("\nMANUAL LABEL STATUS:")
print("Assigned labels: 0")
print("Unlabelled sections:", len(review))

print("\nIMPORTANT NOTES:")
print("- All manual labels are blank.")
print("- No rule-based priority calculation was used.")
print("- Planned work does not confirm actual damage.")
print("- Road-level features repeat across sections.")
print("- No original files or trained models were changed.")

print("\nDONE!")
