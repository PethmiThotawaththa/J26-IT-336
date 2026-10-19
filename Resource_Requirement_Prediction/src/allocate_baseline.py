from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "data/demo"
OUT = ROOT / "outputs/baseline_allocation.csv"

def main():
    tasks = pd.read_csv(DEMO / "maintenance_tasks.csv")
    reqs = pd.read_csv(DEMO / "task_requirements.csv")
    avail = pd.read_csv(DEMO / "resource_availability.csv")

    # Demonstration-only greedy baseline: higher priority first.
    # A task-resource row is fully satisfied or marked short; partial-task
    # semantics must be agreed with a road-maintenance expert for real data.
    remaining = dict(zip(avail["resource_name"], avail["available_quantity"]))
    unit_map = dict(zip(avail["resource_name"], avail["unit"]))
    priority_map = dict(zip(tasks["task_id"], tasks["priority"]))
    reqs["priority"] = reqs["task_id"].map(priority_map)
    reqs = reqs.sort_values(["priority", "task_id"], ascending=[False, True])

    rows = []
    for _, r in reqs.iterrows():
        name = r["resource_name"]
        demand = float(r["required_quantity"])
        supply = float(remaining.get(name, 0))
        compatible_unit = unit_map.get(name) == r["unit"]
        allocated = min(demand, supply) if compatible_unit else 0.0
        remaining[name] = supply - allocated if compatible_unit else supply
        shortage = demand - allocated
        rows.append({
            "task_id": r["task_id"],
            "priority": r["priority"],
            "resource_type": r["resource_type"],
            "resource_name": name,
            "required_quantity": demand,
            "allocated_quantity": allocated,
            "unit": r["unit"],
            "shortage_quantity": shortage,
            "unit_match": compatible_unit,
            "data_status": r["data_status"],
            "note": "DEMO ONLY - invented values; not an RDA recommendation"
                    if str(r["data_status"]).upper() == "SIMULATED"
                    else "Review source status and feasibility",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(rows)
    result.to_csv(OUT, index=False)
    print(result.to_string(index=False))
    print(f"\nSaved: {OUT}")
    print("\nWARNING: This is a simple baseline, not NSGA-II and not a research result.")

if __name__ == "__main__":
    main()
