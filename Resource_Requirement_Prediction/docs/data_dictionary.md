# Data dictionary and provenance rules

## 1. maintenance_tasks.csv

One row per repair task or work package.

| Field | Meaning |
|---|---|
| task_id | Unique task identifier |
| road_id | Road identifier as recorded in the source |
| road_section | Chainage or section description |
| repair_type | Maintenance activity |
| priority | Numeric priority; higher means more urgent in this starter |
| quantity | Work quantity, e.g. area or length |
| quantity_unit | Unit for quantity |
| planned_start | Optional date |
| source_id | Key into source_register.csv |
| data_status | ACTUAL or ESTIMATE |
| notes | Caveats, mapping decisions, missing details |

## 2. task_requirements.csv

One row per task-resource pair.

| Field | Meaning |
|---|---|
| task_id | Key into maintenance_tasks |
| resource_type | LABOUR, MATERIAL, or EQUIPMENT |
| resource_name | Specific resource, e.g. skilled_worker, asphalt_mix, roller |
| required_quantity | Quantity needed for this task |
| unit | person_days, tonnes, litres, machine_hours, etc. |
| data_status | ACTUAL or ESTIMATE |
| source_id | Source of the quantity |
| notes | Calculation method or caveats |

Do not combine unlike units. For example, skilled and unskilled workers should be
separate resource names if they have different availability/skills. Material
types must also be separate.

## 3. resource_availability.csv

One row per resource type and planning period.

| Field | Meaning |
|---|---|
| resource_name | Must match task_requirements.resource_name |
| available_quantity | Quantity available for the selected planning horizon |
| unit | Same unit as requirements |
| planning_period | e.g. 2026-11 or a named planning window |
| source_id | Source of availability |
| data_status | ACTUAL or ESTIMATE |
| notes | Date, office, stock assumptions, constraints |

Do not assume a procurement notice proves current stock. Confirm availability and
the time period from an authorized source.

## 4. source_register.csv

Record the source name, source type, date, page/sheet, source status, access
permission, and any interpretation notes. Never publish confidential material
or identifiable/personal information in the shared repository.

## Data-status definitions

- ACTUAL: verified record of resource use on a completed job, with traceable source.
- ESTIMATE: budget estimate, forecast, tender BOQ, planned quantity, or calculated
  requirement based on approved rates.
- SIMULATED: invented values used only to test software. Do not mix with research data.
- UNKNOWN: source status cannot yet be verified. Resolve before training or evaluation.

The starter uses ACTUAL and ESTIMATE in its core templates. Add SIMULATED only in
test/demo data; do not train an actual-use model on simulated rows.
