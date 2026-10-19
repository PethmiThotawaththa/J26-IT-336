
from pathlib import Path
import re
import pandas as pd


# ==================================================
# 1. FILE PATHS
# ==================================================

ANNOTATION_FILE = Path(
    "outputs/manual_priority_annotation_template.csv"
)

BUDGET_FILE = Path(
    "outputs/section_budget_evidence.csv"
)

OUTPUT_FILE = Path(
    "outputs/priority_annotation_review.csv"
)


# ==================================================
# 2. ROAD ID NORMALIZATION
# ==================================================

def normalize_road_id(value):

    if pd.isna(value):
        return None

    road_id = str(value).strip().upper()

    match = re.fullmatch(r"B0*(\d+)", road_id)

    if match:
        return f"B{int(match.group(1)):03d}"

    return road_id


# ==================================================
# 3. CHECK INPUT FILES
# ==================================================

print("=" * 65)
print("PREPARING PRIORITY ANNOTATION REVIEW DATASET")
print("=" * 65)

for file_path in [ANNOTATION_FILE, BUDGET_FILE]:

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )


# ==================================================
# 4. LOAD DATA
# ==================================================

annotation = pd.read_csv(ANNOTATION_FILE)
budget = pd.read_csv(BUDGET_FILE)

print("\nAnnotation sections:", len(annotation))
print("Section budget records:", len(budget))


# ==================================================
# 5. VALIDATE AND CLEAN SECTION KEYS
# ==================================================

section_keys = [
    "road_id",
    "section_start_m",
    "section_end_m",
]

for dataset_name, df in [
    ("Annotation", annotation),
    ("Budget", budget),
]:

    missing = [
        col for col in section_keys
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{dataset_name} missing columns: {missing}"
        )

    df["road_id"] = (
        df["road_id"].apply(normalize_road_id)
    )

    for column in [
        "section_start_m",
        "section_end_m",
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    if df[section_keys].isna().any().any():
        raise ValueError(
            f"{dataset_name} has missing section identifiers"
        )

    if df.duplicated(subset=section_keys).any():
        raise ValueError(
            f"{dataset_name} has duplicate road sections"
        )


# ==================================================
# 6. SELECT SECTION-LEVEL BUDGET FEATURES
# ==================================================

budget_columns = [
    "section_forecast_budget_lkr",
    "section_budget_work_item_count",
    "section_budget_amounts_missing",
    "section_forecast_budget_per_km_lkr",
]

missing_budget_columns = [
    col for col in budget_columns
    if col not in budget.columns
]

if missing_budget_columns:
    raise ValueError(
        "Missing budget feature columns: "
        f"{missing_budget_columns}"
    )

# Prevent duplicate feature columns if script is rerun
annotation = annotation.drop(
    columns=budget_columns,
    errors="ignore"
)

budget_selected = budget[
    section_keys + budget_columns
].copy()


# ==================================================
# 7. MERGE SECTION BUDGET WITH ANNOTATION
# ==================================================

review = annotation.merge(
    budget_selected,
    on=section_keys,
    how="left",
    validate="one_to_one",
    indicator=True
)

unmatched = review[
    review["_merge"] != "both"
]

if not unmatched.empty:
    raise ValueError(
        "Some annotation sections have no matching "
        "section budget evidence."
    )

review = review.drop(columns=["_merge"])

if len(review) != len(annotation):
    raise ValueError(
        "Section count changed unexpectedly after merge."
    )


# ==================================================
# 8. PRESERVE BLANK MANUAL LABELS
# ==================================================

manual_columns = [
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
    "evidence_reviewed",
    "annotator_id",
    "annotation_date",
]

for column in manual_columns:

    if column not in review.columns:
        review[column] = ""

# Never generate labels automatically.
# Existing manually entered labels, if any,
# are preserved.


# ==================================================
# 9. ORGANIZE REVIEW COLUMNS
# ==================================================

preferred_columns = [
    "section_id",
    "road_id",
    "section_start_m",
    "section_end_m",
    "section_length_m",
    "road_name",
    "road_length_km",

    # Traffic - road-level
    "traffic_mean_vehicles_per_hour",

    # Budget - section-level
    "section_forecast_budget_lkr",
    "section_forecast_budget_per_km_lkr",
    "section_budget_work_item_count",
    "section_budget_amounts_missing",

    # Important locations - road-level
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "nearest_hospital_distance_m",

    # Manual annotation
    "priority_label",
    "annotation_confidence",
    "annotation_reason",
    "evidence_reviewed",
    "annotator_id",
    "annotation_date",
    "annotation_target",
    "damage_severity_status",
]

first_columns = [
    col for col in preferred_columns
    if col in review.columns
]

remaining_columns = [
    col for col in review.columns
    if col not in first_columns
]

review = review[
    first_columns + remaining_columns
]

review = review.sort_values(
    section_keys
).reset_index(drop=True)


# ==================================================
# 10. SAFELY SAVE NEW REVIEW FILE
# ==================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

# Do not overwrite an existing review file.
# It might contain manual annotation work.
if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"\nReview file already exists: {OUTPUT_FILE}\n"
        "It was NOT overwritten. Rename or back up "
        "the existing file before running again."
    )

review.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==================================================
# 11. DISPLAY RESULTS
# ==================================================

print("\n" + "=" * 65)
print("PRIORITY ANNOTATION REVIEW DATASET CREATED")
print("=" * 65)

print("\nOutput file:", OUTPUT_FILE)
print("Total road sections:", len(review))
print("Total columns:", len(review.columns))

print("\nSECTION-LEVEL EVIDENCE:")

display_columns = [
    "section_id",
    "section_forecast_budget_lkr",
    "section_forecast_budget_per_km_lkr",
    "section_budget_work_item_count",
]

print(
    review[display_columns].to_string(
        index=False
    )
)

print("\nMANUAL ANNOTATION STATUS:")

assigned_labels = (
    review["priority_label"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
    .sum()
)

print("Assigned priority labels:", assigned_labels)
print("Total sections:", len(review))

print("\nIMPORTANT NOTES:")
print("- No priority labels were generated.")
print("- Section budgets are forecasts, not actual costs.")
print("- Traffic and location features are road-level.")
print("- Weather does not vary across these six roads.")
print("- Damage severity is still pending.")
print("- Existing ML models remain unchanged.")

print("\nDONE!")
