
from pathlib import Path
import pandas as pd
import re


# ============================================================
# STEP 27 - SUPERVISED ML FEATURE & LEAKAGE AUDIT
#
# READ ONLY
# NO MODEL TRAINING
# NO AUTOMATIC LABEL GENERATION
# NO EXISTING FILE MODIFICATION
# ============================================================

OUTPUTS_DIR = Path("outputs")

ANNOTATIONS_FILE = OUTPUTS_DIR / (
    "priority_annotations_all_confidence_completed.csv"
)

EVIDENCE_FILES = {
    "complete_priority_evidence_review":
        OUTPUTS_DIR / "complete_priority_evidence_review.csv",

    "section_damage_related_maintenance_features":
        OUTPUTS_DIR / (
            "section_damage_related_maintenance_features.csv"
        ),

    "road_priority_features_combined_unlabelled":
        OUTPUTS_DIR / (
            "road_priority_features_combined_unlabelled.csv"
        ),
}

EXPECTED_SECTIONS = {
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

EXPECTED_LABELS = {"High", "Medium", "Low"}


# ============================================================
# 1. HELPER FUNCTIONS
# ============================================================

def section_to_road(section_id):
    """
    Example:
    B047_0_3680 -> B047
    """
    return str(section_id).split("_")[0]


def normalized_column_name(column):
    """
    Normalize names for safer feature classification.
    """
    name = str(column).strip().lower()
    return re.sub(r"[^a-z0-9]+", "_", name).strip("_")


def classify_column(column):
    """
    Conservative audit classification.

    This function classifies COLUMNS only.
    It NEVER generates target labels.
    """

    name = normalized_column_name(column)

    # --------------------------------------------------------
    # Identifiers / location references
    # --------------------------------------------------------

    if name in {
        "section_id",
        "road_id",
        "road_name",
        "road_number",
    }:
        return (
            "IDENTIFIER",
            "Use for joins/grouping, not as ML predictor."
        )

    # --------------------------------------------------------
    # Human target and annotation metadata
    # --------------------------------------------------------

    annotation_keywords = [
        "priority_label",
        "priority_class",
        "priority_target",
        "annotation",
        "annotator",
        "human_reason",
        "human_confidence",
        "evidence_reviewed",
        "additional_observations",
        "ai_recommendation",
        "ai_confidence",
        "review_notes",
        "review_status",
    ]

    if any(
        keyword in name
        for keyword in annotation_keywords
    ):
        return (
            "EXCLUDE_ANNOTATION",
            "Target, AI suggestion or annotation metadata."
        )

    if name in {
        "priority",
        "repair_priority",
        "maintenance_priority",
        "inspection_priority",
    }:
        return (
            "EXCLUDE_TARGET_LIKE",
            "Potential target or target-derived field."
        )

    # --------------------------------------------------------
    # Possible damage fields
    # --------------------------------------------------------

    damage_keywords = [
        "damage",
        "pothole_count",
        "crack_count",
        "rut_depth",
        "roughness",
        "pavement_condition",
        "severity",
        "distress",
    ]

    if any(
        keyword in name
        for keyword in damage_keywords
    ):
        return (
            "REVIEW_DAMAGE_OR_WORK",
            "Verify actual measured damage versus "
            "planned maintenance work."
        )

    # --------------------------------------------------------
    # Planned maintenance / forecast budget
    # --------------------------------------------------------

    maintenance_keywords = [
        "forecast",
        "budget",
        "planned",
        "maintenance",
        "overlay",
        "patching",
        "sealing",
        "work_item",
        "work_type",
        "work_count",
        "work_description",
        "pavement_work",
    ]

    if any(
        keyword in name
        for keyword in maintenance_keywords
    ):
        return (
            "REVIEW_PLANNED_WORK",
            "Planned work / forecast budget; "
            "not verified damage or repair cost."
        )

    # --------------------------------------------------------
    # Traffic fields
    # --------------------------------------------------------

    if any(
        keyword in name
        for keyword in [
            "traffic",
            "vehicle",
            "aadt",
        ]
    ):
        return (
            "REVIEW_ROAD_LEVEL",
            "Check observation duration and road-level "
            "repetition; do not assume AADT."
        )

    # --------------------------------------------------------
    # Nearby important locations
    # --------------------------------------------------------

    poi_keywords = [
        "hospital",
        "school",
        "police",
        "nearby",
        "poi",
        "important_location",
        "nearest",
        "distance",
    ]

    if any(
        keyword in name
        for keyword in poi_keywords
    ):
        return (
            "REVIEW_ROAD_LEVEL",
            "Nearby-location feature may be road-level "
            "and repeated across sections."
        )

    # --------------------------------------------------------
    # Other columns
    # --------------------------------------------------------

    return (
        "MANUAL_REVIEW",
        "Inspect meaning, source, timing and missing values."
    )


def print_separator():
    print("=" * 70)


# ============================================================
# 2. LOAD FINAL HUMAN ANNOTATIONS
# ============================================================

print_separator()
print("STEP 27 - SUPERVISED ML FEATURE & LEAKAGE AUDIT")
print_separator()

if not ANNOTATIONS_FILE.is_file():
    raise FileNotFoundError(
        f"Missing annotation file: {ANNOTATIONS_FILE}"
    )

annotations = pd.read_csv(
    ANNOTATIONS_FILE,
    dtype={"section_id": "string"}
)

print("\nANNOTATION DATASET")
print("File:", ANNOTATIONS_FILE)
print("Rows:", len(annotations))
print("Columns:", len(annotations.columns))


# ============================================================
# 3. VALIDATE SECTION IDs AND LABELS
# ============================================================

required_columns = [
    "section_id",
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
]

missing_columns = [
    col for col in required_columns
    if col not in annotations.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required annotation columns: "
        f"{missing_columns}"
    )

if len(annotations) != 9:
    raise ValueError(
        f"Expected 9 annotated sections, "
        f"found {len(annotations)}."
    )

if annotations["section_id"].isna().any():
    raise ValueError("Missing section IDs.")

if annotations["section_id"].duplicated().any():
    raise ValueError("Duplicate section IDs.")

if set(annotations["section_id"]) != EXPECTED_SECTIONS:
    raise ValueError(
        "Annotated section IDs do not match "
        "the expected nine sections."
    )

labels = (
    annotations["priority_label"]
    .astype("string")
    .str.strip()
)

if not labels.isin(EXPECTED_LABELS).all():
    raise ValueError(
        "Invalid or missing human priority labels."
    )

print("\nHuman labels: VALID")

print(
    labels.value_counts()
    .reindex(
        ["High", "Medium", "Low"],
        fill_value=0
    )
    .to_string()
)


# ============================================================
# 4. CHECK NUMBER OF INDEPENDENT ROADS
# ============================================================

annotations["audit_road_id"] = (
    annotations["section_id"]
    .map(section_to_road)
)

road_counts = (
    annotations["audit_road_id"]
    .value_counts()
    .sort_index()
)

print("\nINDEPENDENT ROAD GROUPS")
print("Unique roads:", road_counts.size)
print("Total sections:", len(annotations))

print("\nSections per road:")
print(road_counts.to_string())

if road_counts.size < len(annotations):
    print(
        "\nWARNING: Some roads have multiple sections. "
        "Road-level features can repeat across rows."
    )


# ============================================================
# 5. CHECK ANNOTATION / AI LEAKAGE COLUMNS
# ============================================================

print("\n")
print_separator()
print("ANNOTATION COLUMN AUDIT")
print_separator()

for column in annotations.columns:
    category, explanation = classify_column(column)

    print(
        f"{column}\n"
        f"  Category: {category}\n"
        f"  Reason: {explanation}"
    )


# ============================================================
# 6. CHECK EXISTING EVIDENCE CSV FILES
# ============================================================

print("\n")
print_separator()
print("EVIDENCE FILE AUDIT")
print_separator()

for dataset_name, file_path in EVIDENCE_FILES.items():

    print("\n" + "-" * 70)
    print("Dataset:", dataset_name)
    print("Path:", file_path)

    if not file_path.is_file():
        print("Status: FILE NOT FOUND")
        continue

    data = pd.read_csv(file_path)

    print("Status: FOUND")
    print("Rows:", len(data))
    print("Columns:", len(data.columns))

    if "section_id" in data.columns:
        print(
            "Unique section IDs:",
            data["section_id"].nunique()
        )

        print(
            "Duplicate section IDs:",
            int(data["section_id"].duplicated().sum())
        )

    elif "road_id" in data.columns:
        print(
            "Unique road IDs:",
            data["road_id"].nunique()
        )

        print(
            "NOTE: Road-level dataset. "
            "Do not treat roads as nine "
            "independent section observations."
        )

    else:
        print(
            "NOTE: No section_id / road_id column "
            "detected with these exact names."
        )

    print("\nCOLUMN AUDIT:")

    for column in data.columns:

        category, explanation = classify_column(column)

        non_missing = int(
            data[column].notna().sum()
        )

        unique_values = int(
            data[column].nunique(dropna=True)
        )

        print(
            f"\n  {column}"
            f"\n    Category: {category}"
            f"\n    Non-missing: {non_missing}/{len(data)}"
            f"\n    Unique values: {unique_values}"
            f"\n    Note: {explanation}"
        )


# ============================================================
# 7. CHECK HUMAN / AI AGREEMENT
# ============================================================

print("\n")
print_separator()
print("HUMAN / AI AGREEMENT - DESCRIPTIVE ONLY")
print_separator()

if "ai_recommendation" in annotations.columns:

    ai_labels = (
        annotations["ai_recommendation"]
        .astype("string")
        .str.strip()
    )

    agreement = int(
        labels.eq(ai_labels).fillna(False).sum()
    )

    print(
        f"Human-AI agreement: "
        f"{agreement}/{len(annotations)}"
    )

    print(
        "This is NOT ML accuracy. "
        "The AI recommendation was visible "
        "during human annotation."
    )


# ============================================================
# 8. PRINT LEAKAGE SAFETY GUIDANCE
# ============================================================

print("\n")
print_separator()
print("SUPERVISED ML READINESS SUMMARY")
print_separator()

print("\nHuman-labelled sections:", len(annotations))
print("Independent road groups:", road_counts.size)

print("\nDO NOT USE AS MODEL INPUT FEATURES:")
print("- priority_label (this is the target)")
print("- annotation_confidence")
print("- annotation_reason")
print("- annotation_target")
print("- annotator_id / annotation_date")
print("- evidence_reviewed")
print("- additional_observations")
print("- ai_recommendation")
print("- ai_recommendation_confidence")
print("- any derived priority score or priority rank")

print("\nFEATURES THAT REQUIRE REVIEW:")
print("- Road-level traffic features")
print("- Road-level nearby-location counts/distances")
print("- Section-level planned pavement work")
print("- Section-level forecast maintenance budget")
print("- Actual damage fields, if present")

print("\nSCIENTIFIC LIMITATIONS:")
print("- Only nine human-labelled sections.")
print("- Six road groups, not nine independent roads.")
print("- Road-level features repeat across sections.")
print("- Planned work is not verified road damage.")
print("- Forecast budget is not actual repair cost.")
print("- Traffic observations are not AADT.")
print("- Actual damage severity is unavailable.")
print("- AI suggestions were visible during labeling.")
print("- No reliable generalization accuracy can")
print("  be claimed from this dataset alone.")

print("\nNO FILES WERE MODIFIED.")
print("NO LABELS WERE GENERATED.")
print("NO MODELS WERE TRAINED.")

print("\nDONE!")
