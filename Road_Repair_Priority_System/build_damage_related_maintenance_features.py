
from pathlib import Path
import re

import pandas as pd


# ============================================================
# STEP 11: DAMAGE-RELATED MAINTENANCE FEATURES
# ============================================================

BUDGET_FILE = Path(
    "datasets/Forecasted routine maintenance budget 2026.xlsx"
)

ANNOTATION_FILE = Path(
    "outputs/priority_annotation_review.csv"
)

FEATURES_OUTPUT = Path(
    "outputs/section_damage_related_maintenance_features.csv"
)

REVIEW_OUTPUT = Path(
    "outputs/priority_annotation_review_with_damage_work.csv"
)


# ============================================================
# 1. RMMS CODE MAPPING
# Based on the uploaded RMMS maintenance items image.
# ============================================================

DAMAGE_RELATED_ITEMS = {
    1: "Patching potholes",
    2: "Crack sealing",
    3: "Edge correction",
    57: "Repairing of ruts, depression and surface irregularities",
    73: "Sand sealing",
    74: "Chip sealing",
    75: "Section overlay",
    76: "Surface milling",
    77: "Base failure correction",
}

# These codes indicate planned pavement maintenance.
# They do NOT provide confirmed damage severity.


# ============================================================
# 2. NORMALIZE ROAD IDs
# ============================================================

def normalize_road_id(value):

    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    match = re.fullmatch(r"B0*(\d+)", value)

    if match:
        return f"B{int(match.group(1)):03d}"

    return value


# ============================================================
# 3. CHECK FILES
# ============================================================

for file_path in [BUDGET_FILE, ANNOTATION_FILE]:

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

# Protect existing annotation work.
for output_file in [FEATURES_OUTPUT, REVIEW_OUTPUT]:

    if output_file.exists():
        raise FileExistsError(
            f"Output file already exists: {output_file}\n"
            "File was NOT overwritten."
        )


# ============================================================
# 4. LOAD DATA
# ============================================================

budget = pd.read_excel(
    BUDGET_FILE,
    sheet_name="Budget"
)

review = pd.read_csv(
    ANNOTATION_FILE
)

print("=" * 65)
print("DAMAGE-RELATED MAINTENANCE FEATURE PREPARATION")
print("=" * 65)

print("\nTotal budget work items:", len(budget))
print("Total annotation sections:", len(review))


# ============================================================
# 5. VALIDATE REQUIRED COLUMNS
# ============================================================

required_budget_columns = [
    "RoadID",
    "StartChainage(m)",
    "EndChainage(m)",
    "Item Code",
    "Total Amount (Rs.)",
]

missing = [
    col
    for col in required_budget_columns
    if col not in budget.columns
]

if missing:
    raise ValueError(
        f"Missing budget columns: {missing}"
    )


# ============================================================
# 6. CLEAN BUDGET DATA
# ============================================================

budget["road_id"] = (
    budget["RoadID"].apply(normalize_road_id)
)

budget["section_start_m"] = pd.to_numeric(
    budget["StartChainage(m)"],
    errors="coerce"
)

budget["section_end_m"] = pd.to_numeric(
    budget["EndChainage(m)"],
    errors="coerce"
)

budget["item_code"] = pd.to_numeric(
    budget["Item Code"],
    errors="coerce"
)

budget["item_amount_lkr"] = pd.to_numeric(
    budget["Total Amount (Rs.)"],
    errors="coerce"
)

budget = budget.dropna(
    subset=[
        "road_id",
        "section_start_m",
        "section_end_m",
    ]
).copy()

budget = budget[
    budget["section_end_m"]
    > budget["section_start_m"]
].copy()


# ============================================================
# 7. FILTER ONLY SELECTED DAMAGE-RELATED ITEMS
# ============================================================

damage_work = budget[
    budget["item_code"].isin(
        DAMAGE_RELATED_ITEMS.keys()
    )
].copy()

damage_work["item_description"] = (
    damage_work["item_code"]
    .map(DAMAGE_RELATED_ITEMS)
)

print("\nSelected damage-related item codes:")
print(sorted(DAMAGE_RELATED_ITEMS.keys()))

print("\nDamage-related budget rows found:", len(damage_work))

print("\nMATCHED ITEM CODES:")

if damage_work.empty:
    print("No selected items found.")
else:
    print(
        damage_work["item_code"]
        .value_counts()
        .sort_index()
        .to_string()
    )


# ============================================================
# 8. PREPARE SECTION-LEVEL FEATURES
# ============================================================

section_keys = [
    "road_id",
    "section_start_m",
    "section_end_m",
]

# Use the actual 9 annotation sections as the master list.
sections = review[section_keys].copy()

sections["road_id"] = (
    sections["road_id"].apply(normalize_road_id)
)

for column in [
    "section_start_m",
    "section_end_m",
]:
    sections[column] = pd.to_numeric(
        sections[column],
        errors="coerce"
    )

if sections[section_keys].isna().any().any():
    raise ValueError(
        "Annotation review contains missing section keys."
    )

if sections.duplicated(subset=section_keys).any():
    raise ValueError(
        "Duplicate sections found in annotation review."
    )


# Count selected work items per section.
if damage_work.empty:

    section_summary = sections.copy()

    section_summary["damage_related_work_item_count"] = 0
    section_summary["damage_related_forecast_budget_lkr"] = 0.0
    section_summary["damage_related_amounts_missing"] = 0

else:

    section_summary = (
        damage_work.groupby(
            section_keys,
            as_index=False
        )
        .agg(
            damage_related_work_item_count=(
                "item_code",
                "size"
            ),
            damage_related_forecast_budget_lkr=(
                "item_amount_lkr",
                "sum"
            ),
            damage_related_amounts_missing=(
                "item_amount_lkr",
                lambda x: int(x.isna().sum())
            ),
        )
    )

    # If some selected work items have no amount,
    # do not present the partial sum as a complete total.
    section_summary.loc[
        section_summary["damage_related_amounts_missing"] > 0,
        "damage_related_forecast_budget_lkr"
    ] = float("nan")

    section_summary = sections.merge(
        section_summary,
        on=section_keys,
        how="left",
        validate="one_to_one"
    )

    section_summary["damage_related_work_item_count"] = (
        section_summary["damage_related_work_item_count"]
        .fillna(0)
        .astype(int)
    )

    section_summary["damage_related_forecast_budget_lkr"] = (
        section_summary["damage_related_forecast_budget_lkr"]
        .fillna(0)
        .astype(float)
    )

    section_summary["damage_related_amounts_missing"] = (
        section_summary["damage_related_amounts_missing"]
        .fillna(0)
        .astype(int)
    )

    # Restore NaN for incomplete totals.
    section_summary.loc[
        section_summary["damage_related_amounts_missing"] > 0,
        "damage_related_forecast_budget_lkr"
    ] = float("nan")


# ============================================================
# 9. ADD INDIVIDUAL ITEM FLAGS AND COUNTS
# ============================================================

for item_code, description in DAMAGE_RELATED_ITEMS.items():

    count_column = f"planned_item_{item_code}_count"
    flag_column = f"planned_item_{item_code}_present"

    selected = damage_work[
        damage_work["item_code"] == item_code
    ]

    if selected.empty:

        section_summary[count_column] = 0

    else:

        counts = (
            selected.groupby(section_keys)
            .size()
            .reset_index(name=count_column)
        )

        section_summary = section_summary.merge(
            counts,
            on=section_keys,
            how="left",
            validate="one_to_one"
        )

        section_summary[count_column] = (
            section_summary[count_column]
            .fillna(0)
            .astype(int)
        )

    section_summary[flag_column] = (
        section_summary[count_column] > 0
    ).astype(int)


# ============================================================
# 10. ADD HUMAN-READABLE DESCRIPTIONS
# ============================================================

if damage_work.empty:

    section_summary["planned_damage_work_descriptions"] = ""

else:

    descriptions = (
        damage_work.groupby(section_keys)[
            "item_description"
        ]
        .apply(
            lambda values: "; ".join(
                sorted(set(values.dropna()))
            )
        )
        .reset_index(
            name="planned_damage_work_descriptions"
        )
    )

    section_summary = section_summary.merge(
        descriptions,
        on=section_keys,
        how="left",
        validate="one_to_one"
    )

    section_summary["planned_damage_work_descriptions"] = (
        section_summary["planned_damage_work_descriptions"]
        .fillna("")
    )


# ============================================================
# 11. VALIDATE AND MERGE WITH ANNOTATION REVIEW
# ============================================================

review["road_id"] = (
    review["road_id"].apply(normalize_road_id)
)

for column in [
    "section_start_m",
    "section_end_m",
]:
    review[column] = pd.to_numeric(
        review[column],
        errors="coerce"
    )

new_feature_columns = [
    col
    for col in section_summary.columns
    if col not in section_keys
]

overlapping = [
    col
    for col in new_feature_columns
    if col in review.columns
]

if overlapping:
    raise ValueError(
        "Feature columns already exist in annotation review: "
        f"{overlapping}"
    )

combined = review.merge(
    section_summary,
    on=section_keys,
    how="left",
    validate="one_to_one",
    indicator=True
)

if (combined["_merge"] != "both").any():
    raise ValueError(
        "Some annotation sections did not match."
    )

combined = combined.drop(columns=["_merge"])

if len(combined) != len(review):
    raise ValueError(
        "Section count changed after merging."
    )


# ============================================================
# 12. SAVE NEW FILES
# ============================================================

FEATURES_OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

section_summary.to_csv(
    FEATURES_OUTPUT,
    index=False
)

combined.to_csv(
    REVIEW_OUTPUT,
    index=False
)


# ============================================================
# 13. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 65)
print("DAMAGE-RELATED MAINTENANCE FEATURES CREATED")
print("=" * 65)

print("\nFeature file:", FEATURES_OUTPUT)
print("Review file:", REVIEW_OUTPUT)

print("\nTotal sections:", len(section_summary))
print("Total combined columns:", len(combined.columns))

print("\nSECTION SUMMARY:")

display_columns = [
    "road_id",
    "section_start_m",
    "section_end_m",
    "damage_related_work_item_count",
    "damage_related_forecast_budget_lkr",
    "planned_item_1_present",
    "planned_item_2_present",
    "planned_item_75_present",
]

print(
    section_summary[
        display_columns
    ].to_string(index=False)
)

print("\nIMPORTANT NOTES:")
print("- Features represent PLANNED maintenance activities.")
print("- They are not confirmed detected damage.")
print("- They are not damage severity scores.")
print("- No priority labels were generated.")
print("- Existing annotation labels were preserved.")
print("- Existing trained ML models were not modified.")

print("\nDONE!")
