
from pathlib import Path
import re
import pandas as pd


# ==================================================
# 1. FILE PATHS
# ==================================================

BUDGET_FILE = Path(
    "datasets/Forecasted routine maintenance budget 2026.xlsx"
)

ANNOTATION_FILE = Path(
    "outputs/manual_priority_annotation_template.csv"
)

OUTPUT_FILE = Path(
    "outputs/section_budget_evidence.csv"
)


# ==================================================
# 2. NORMALIZE ROAD IDs
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
# 3. LOAD DATA
# ==================================================

for file in [BUDGET_FILE, ANNOTATION_FILE]:
    if not file.exists():
        raise FileNotFoundError(
            f"Required file not found: {file}"
        )

budget = pd.read_excel(
    BUDGET_FILE,
    sheet_name="Budget"
)

annotation = pd.read_csv(
    ANNOTATION_FILE
)

required_columns = [
    "RoadID",
    "StartChainage(m)",
    "EndChainage(m)",
    "Total Amount (Rs.)",
]

missing = [
    col for col in required_columns
    if col not in budget.columns
]

if missing:
    raise ValueError(
        f"Missing budget columns: {missing}"
    )


# ==================================================
# 4. CLEAN BUDGET DATA
# ==================================================

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

budget["budget_amount_lkr"] = pd.to_numeric(
    budget["Total Amount (Rs.)"],
    errors="coerce"
)

budget = budget.dropna(
    subset=[
        "road_id",
        "section_start_m",
        "section_end_m",
    ]
)

budget = budget[
    budget["section_end_m"]
    > budget["section_start_m"]
].copy()


# ==================================================
# 5. SUMMARIZE EACH SECTION
# ==================================================

section_budget = (
    budget.groupby(
        [
            "road_id",
            "section_start_m",
            "section_end_m",
        ],
        as_index=False
    )
    .agg(
        section_forecast_budget_lkr=(
            "budget_amount_lkr",
            "sum"
        ),
        section_budget_work_item_count=(
            "budget_amount_lkr",
            "size"
        ),
        section_budget_amounts_missing=(
            "budget_amount_lkr",
            lambda x: int(x.isna().sum())
        ),
    )
)

section_budget["section_length_m"] = (
    section_budget["section_end_m"]
    - section_budget["section_start_m"]
)

section_budget["section_forecast_budget_per_km_lkr"] = (
    section_budget["section_forecast_budget_lkr"]
    / (section_budget["section_length_m"] / 1000)
)

# Budget totals are incomplete if any work item amount is missing.
incomplete = (
    section_budget["section_budget_amounts_missing"] > 0
)

section_budget.loc[
    incomplete,
    [
        "section_forecast_budget_lkr",
        "section_forecast_budget_per_km_lkr",
    ]
] = float("nan")


# ==================================================
# 6. VALIDATE AGAINST ANNOTATION SECTIONS
# ==================================================

section_keys = [
    "road_id",
    "section_start_m",
    "section_end_m",
]

annotation["road_id"] = (
    annotation["road_id"].apply(normalize_road_id)
)

for col in ["section_start_m", "section_end_m"]:
    annotation[col] = pd.to_numeric(
        annotation[col],
        errors="coerce"
    )

annotation_sections = annotation[
    section_keys
].drop_duplicates()

validation = annotation_sections.merge(
    section_budget[section_keys],
    on=section_keys,
    how="left",
    indicator=True,
    validate="one_to_one"
)

if (validation["_merge"] != "both").any():
    raise ValueError(
        "Some annotation sections do not match "
        "the budget sections."
    )


# ==================================================
# 7. SAVE SECTION BUDGET EVIDENCE
# ==================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

section_budget = section_budget.sort_values(
    section_keys
)

section_budget.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==================================================
# 8. DISPLAY RESULTS
# ==================================================

print("\n" + "=" * 65)
print("SECTION-LEVEL BUDGET EVIDENCE COMPLETED")
print("=" * 65)

print("\nOutput file:", OUTPUT_FILE)
print("Total sections:", len(section_budget))
print("Original budget work-item rows:", len(budget))

print("\nSECTION BUDGET SUMMARY:")

print(
    section_budget[
        [
            "road_id",
            "section_start_m",
            "section_end_m",
            "section_forecast_budget_lkr",
            "section_budget_work_item_count",
            "section_forecast_budget_per_km_lkr",
        ]
    ].to_string(index=False)
)

print("\nIMPORTANT:")
print("- These are forecast maintenance budget amounts.")
print("- They are not actual repair costs.")
print("- They are not repair-priority labels.")
print("- No trained models or original files were modified.")
