
from pathlib import Path
import re
import pandas as pd


# ==================================================
# 1. FILE PATHS
# ==================================================

BUDGET_FILE = Path(
    "datasets/Forecasted routine maintenance budget 2026.xlsx"
)

FEATURES_FILE = Path(
    "outputs/road_priority_features_combined_unlabelled.csv"
)

OUTPUT_FILE = Path(
    "outputs/manual_priority_annotation_template.csv"
)


# ==================================================
# 2. NORMALIZE ROAD IDS
# ==================================================

def normalize_road_id(value):
    """
    Convert road IDs to a common format.

    Examples:
        B0047 -> B047
        B0174 -> B174
        B0214 -> B214
        B0240 -> B240
        B0263 -> B263
        B0435 -> B435
    """

    if pd.isna(value):
        return None

    road_id = str(value).strip().upper()

    match = re.fullmatch(r"B0*(\d+)", road_id)

    if match:
        road_number = int(match.group(1))
        return f"B{road_number:03d}"

    return road_id


# ==================================================
# 3. CHECK INPUT FILES
# ==================================================

print("=" * 60)
print("CREATING MANUAL PRIORITY ANNOTATION TEMPLATE")
print("=" * 60)

for file_path in [BUDGET_FILE, FEATURES_FILE]:

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required input file not found: {file_path}"
        )

print("\nInput files found successfully.")


# ==================================================
# 4. LOAD RDA BUDGET DATA
# ==================================================

budget = pd.read_excel(
    BUDGET_FILE,
    sheet_name="Budget"
)

print("\nRDA Budget rows loaded:", len(budget))

required_budget_columns = [
    "RoadID",
    "StartChainage(m)",
    "EndChainage(m)",
]

missing_budget_columns = [
    col
    for col in required_budget_columns
    if col not in budget.columns
]

if missing_budget_columns:
    raise ValueError(
        "Missing columns in RDA Budget file: "
        f"{missing_budget_columns}"
    )


# ==================================================
# 5. EXTRACT REAL ROAD SECTIONS
# ==================================================

sections = budget[
    required_budget_columns
].copy()

sections = sections.rename(
    columns={
        "RoadID": "road_id",
        "StartChainage(m)": "section_start_m",
        "EndChainage(m)": "section_end_m",
    }
)

# Normalize road IDs
sections["road_id"] = (
    sections["road_id"]
    .apply(normalize_road_id)
)

# Convert chainage values to numbers
sections["section_start_m"] = pd.to_numeric(
    sections["section_start_m"],
    errors="coerce"
)

sections["section_end_m"] = pd.to_numeric(
    sections["section_end_m"],
    errors="coerce"
)

# Remove incomplete records
sections = sections.dropna(
    subset=[
        "road_id",
        "section_start_m",
        "section_end_m",
    ]
)

# Keep valid sections only
sections = sections[
    sections["section_end_m"]
    > sections["section_start_m"]
].copy()

# Remove repeated budget work-item sections
sections = sections.drop_duplicates(
    subset=[
        "road_id",
        "section_start_m",
        "section_end_m",
    ]
)

# Sort road sections
sections = sections.sort_values(
    by=[
        "road_id",
        "section_start_m",
        "section_end_m",
    ]
).reset_index(drop=True)

# Calculate section length
sections["section_length_m"] = (
    sections["section_end_m"]
    - sections["section_start_m"]
)

# Unique section identifier
sections["section_id"] = sections.apply(
    lambda row: (
        f"{row['road_id']}_"
        f"{row['section_start_m']:g}_"
        f"{row['section_end_m']:g}"
    ),
    axis=1
)

print("\nUnique RDA road sections:", len(sections))

print("\nRoad IDs after normalization:")
print(
    sorted(sections["road_id"].unique())
)


# ==================================================
# 6. LOAD COMBINED ROAD FEATURES
# ==================================================

features = pd.read_csv(FEATURES_FILE)

if "road_id" not in features.columns:
    raise ValueError(
        "road_id column missing from combined features"
    )

features["road_id"] = (
    features["road_id"]
    .apply(normalize_road_id)
)

if features["road_id"].isna().any():
    raise ValueError(
        "Missing road IDs found in combined features"
    )

if features["road_id"].duplicated().any():

    duplicate_ids = features.loc[
        features["road_id"].duplicated(),
        "road_id"
    ].tolist()

    raise ValueError(
        "Duplicate road IDs found in combined features: "
        f"{duplicate_ids}"
    )

print("\nCombined feature rows:", len(features))

print("Combined feature columns:", len(features.columns))


# ==================================================
# 7. REMOVE EXISTING TARGET/ANNOTATION COLUMNS
# ==================================================

# The existing priority_label column is empty.
# Remove it before merging to avoid duplicate columns.
# The manual annotation columns will be created below.

annotation_columns = [
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
    "evidence_reviewed",
    "annotator_id",
    "annotation_date",
    "annotation_target",
    "damage_severity_status",
]

features = features.drop(
    columns=annotation_columns,
    errors="ignore"
)


# ==================================================
# 8. MERGE FEATURES WITH ROAD SECTIONS
# ==================================================

annotation = sections.merge(
    features,
    on="road_id",
    how="left",
    validate="many_to_one",
    indicator=True
)

unmatched = annotation[
    annotation["_merge"] != "both"
]

if not unmatched.empty:

    unmatched_ids = sorted(
        unmatched["road_id"].unique().tolist()
    )

    raise ValueError(
        "Some road sections have no matching features: "
        f"{unmatched_ids}"
    )

annotation = annotation.drop(
    columns=["_merge"]
)

print("\nFeature merge successful.")


# ==================================================
# 9. ADD BLANK MANUAL ANNOTATION COLUMNS
# ==================================================

# These fields must be filled after reviewing evidence.
# NO rule-based labels are generated.

annotation["priority_label"] = ""
annotation["annotation_confidence"] = ""
annotation["annotation_reason"] = ""
annotation["evidence_reviewed"] = ""
annotation["annotator_id"] = ""
annotation["annotation_date"] = ""

# Current V1 target - severity is not available yet.
annotation["annotation_target"] = (
    "provisional_maintenance_inspection_priority"
)

annotation["damage_severity_status"] = (
    "pending_component_1"
)


# ==================================================
# 10. ORGANIZE OUTPUT COLUMNS
# ==================================================

first_columns = [
    "section_id",
    "road_id",
    "section_start_m",
    "section_end_m",
    "section_length_m",
    "road_name",
    "road_length_km",
    "traffic_mean_vehicles_per_hour",
    "forecast_2026_budget_lkr",
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "nearest_hospital_distance_m",
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
    "evidence_reviewed",
    "annotator_id",
    "annotation_date",
    "annotation_target",
    "damage_severity_status",
]

existing_first_columns = [
    col
    for col in first_columns
    if col in annotation.columns
]

remaining_columns = [
    col
    for col in annotation.columns
    if col not in existing_first_columns
]

annotation = annotation[
    existing_first_columns + remaining_columns
]


# ==================================================
# 11. SAVE NEW ANNOTATION TEMPLATE
# ==================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

annotation.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==================================================
# 12. PRINT RESULTS
# ==================================================

print("\n" + "=" * 60)
print("MANUAL PRIORITY ANNOTATION TEMPLATE CREATED")
print("=" * 60)

print("\nOutput file:", OUTPUT_FILE)

print("Total unique road sections:", len(annotation))
print("Total columns:", len(annotation.columns))

print("\nSECTIONS BY ROAD:")
print(
    annotation.groupby("road_id")
    .size()
    .to_string()
)

print("\nROAD SECTIONS:")
print(
    annotation[
        [
            "section_id",
            "road_id",
            "section_start_m",
            "section_end_m",
            "section_length_m",
        ]
    ].to_string(index=False)
)

print("\nMANUAL LABEL STATUS:")
print("Priority labels assigned: 0")
print("All priority labels are intentionally blank.")

print("\nANNOTATION TARGET:")
print(
    annotation["annotation_target"].iloc[0]
    if not annotation.empty
    else "No sections available"
)

if len(annotation) < 30:
    print(
        "\nWARNING: Small dataset detected."
        "\nReliable supervised ML training will require"
        "\nmore independently assessed examples."
    )

print("\nIMPORTANT NOTES:")
print("- No priority labels were automatically generated.")
print("- Road-level features are repeated across sections.")
print("- Road-level budget is not section-specific cost.")
print("- Component 1 damage severity is not included.")
print("- Original datasets and trained models are unchanged.")

print("\nDONE!")
