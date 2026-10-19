
from pathlib import Path

import pandas as pd


# ============================================================
# STEP 15 - COMPLETE ROAD PRIORITY EVIDENCE REVIEW
# ============================================================

INPUT_FILE = Path(
    "outputs/priority_annotation_review_with_damage_work.csv"
)

OUTPUT_FILE = Path(
    "outputs/complete_priority_evidence_review.csv"
)


# ============================================================
# 1. CHECK INPUT AND PROTECT EXISTING FILES
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"Output already exists: {OUTPUT_FILE}\n"
        "Existing file was NOT overwritten."
    )


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 80)
print("COMPLETE ROAD SECTION PRIORITY EVIDENCE REVIEW")
print("=" * 80)

print("\nInput sections:", len(df))
print("Input columns:", len(df.columns))


# ============================================================
# 3. SELECT ALL RELEVANT EVIDENCE
# ============================================================

evidence_columns = [

    # Road and section identification
    "section_id",
    "road_id",
    "road_name",
    "section_start_m",
    "section_end_m",
    "section_length_m",

    # Traffic evidence - ROAD LEVEL
    "traffic_observation_count",
    "traffic_mean_vehicles_per_hour",
    "traffic_min_vehicles_per_hour",
    "traffic_max_vehicles_per_hour",

    # Nearby important locations - ROAD LEVEL
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "nearest_hospital_distance_m",
    "nearest_school_distance_m",
    "nearest_police_distance_m",

    # Budget evidence - SECTION LEVEL
    "section_forecast_budget_lkr",
    "section_forecast_budget_per_km_lkr",
    "section_budget_work_item_count",

    # Planned pavement maintenance - SECTION LEVEL
    "damage_related_work_item_count",
    "damage_related_forecast_budget_lkr",
    "planned_item_1_count",
    "planned_item_2_count",
    "planned_item_75_count",
    "planned_damage_work_descriptions",
]

missing_columns = [
    col
    for col in evidence_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        "Required evidence columns missing:\n"
        + "\n".join(missing_columns)
    )

review = df[evidence_columns].copy()


# ============================================================
# 4. VALIDATE SECTION IDENTIFIERS
# ============================================================

if review["section_id"].isna().any():
    raise ValueError(
        "Missing section IDs detected."
    )

if review["section_id"].duplicated().any():
    raise ValueError(
        "Duplicate section IDs detected."
    )


# ============================================================
# 5. ADD MANUAL ANNOTATION FIELDS
# ============================================================

# Intentionally blank.
# No formulas, weights, or automatic labels.

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
# 6. SORT SECTIONS
# ============================================================

review = review.sort_values(
    by=[
        "road_id",
        "section_start_m",
        "section_end_m",
    ]
).reset_index(drop=True)


# ============================================================
# 7. SAVE NEW REVIEW FILE
# ============================================================

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
# 8. PRINT ALL SECTION EVIDENCE
# ============================================================

print("\n" + "=" * 80)
print("TRAFFIC + IMPORTANT LOCATIONS + BUDGET + PAVEMENT WORK")
print("=" * 80)

display_columns = [
    "section_id",
    "traffic_mean_vehicles_per_hour",
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "section_forecast_budget_lkr",
    "planned_damage_work_descriptions",
]

print(
    review[display_columns].to_string(
        index=False,
        max_colwidth=65
    )
)


# ============================================================
# 9. CHECK MISSING EVIDENCE
# ============================================================

print("\n" + "=" * 80)
print("MISSING EVIDENCE CHECK")
print("=" * 80)

print(
    review[evidence_columns]
    .isna()
    .sum()
    .to_string()
)


# ============================================================
# 10. PRINT ANNOTATION STATUS
# ============================================================

print("\n" + "=" * 80)
print("MANUAL ANNOTATION STATUS")
print("=" * 80)

print("Total sections:", len(review))
print("Assigned priority labels: 0")
print("Unlabelled sections:", len(review))

print("\nOUTPUT FILE:")
print(OUTPUT_FILE)

print("\nIMPORTANT:")
print("- Traffic features describe the whole road.")
print("- Nearby location features describe the whole road.")
print("- Section budget and planned work are section-specific.")
print("- Planned work is NOT confirmed road damage.")
print("- No priority labels were generated.")
print("- No trained ML models were modified.")

print("\nDONE!")
