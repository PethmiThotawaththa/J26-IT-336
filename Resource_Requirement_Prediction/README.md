# Road Maintenance Resource Allocation — Starter

This is a beginner-friendly starter for the resource-allocation component of
the SLIIT research project "AI-Driven Multi-Resource Allocation and Planning
for Road Maintenance".

## Important data rule

- `ACTUAL`: verified quantities actually used on a completed task.
- `ESTIMATE`: planned/forecasted/BOQ quantities.
- Never change an estimate to `ACTUAL` just because it appears in a tender or BOQ.
- Do not put confidential RDA documents, private records, or personal data in Git.

## Folder contents

- `data/templates/maintenance_tasks.csv`: one row per repair task.
- `data/templates/task_requirements.csv`: resource demand per task.
- `data/templates/resource_availability.csv`: resource stock/capacity.
- `data/templates/source_register.csv`: provenance/status of every source.
- `src/inspect_data.py`: inspect CSV files and report missing values.
- `src/allocate_baseline.py`: a simple priority-first baseline allocator.
- `src/validate_inputs.py`: check required columns, status values, and resource units.
- `docs/data_dictionary.md`: definitions and data rules.

## Setup in VS Code (Windows PowerShell)

1. Extract this ZIP.
2. Open the extracted `road_maintenance_allocation_starter` folder in VS Code.
3. Open Terminal > New Terminal.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install pandas
   ```

5. Install pandas:
   ```powershell
   python -m pip install pandas
   ```

6. Inspect the templates:
   ```powershell
   python src/inspect_data.py
   python src/validate_inputs.py
   ```

7. Run the demonstration allocator:
   ```powershell
   python src/allocate_baseline.py
   ```
   It reads only the clearly labelled illustrative demo files in `data/demo/`
   and writes `outputs/baseline_allocation.csv`.

## Next: use your own data safely

1. Copy authorized source files to a local folder that is NOT committed to Git.
2. Inspect the workbook sheets/columns first. Do not merge all files immediately.
3. Create normalized CSV exports for repair tasks, resource requirements, and resource availability.
4. Record a source document/page, date, unit, and `data_status` (`ACTUAL` or `ESTIMATE`) for every record.
5. Run the input checks.
6. Compare baseline results with NSGA-II after the baseline is understood and validated.

## What this baseline does (and does not do)

It allocates each resource independently to tasks in descending priority order,
up to available capacity. It is a starting comparison method, not NSGA-II and
not a claim of optimality. The example values are invented solely to test the
code; they are not RDA values or research findings.

For a research-quality optimizer, define objectives and constraints with your
supervisor and domain expert. Examples include task coverage, estimated cost,
resource utilization, and waste. Define how partial tasks are treated and how
equipment hours, labour-days, and material units are represented.
