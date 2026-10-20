from pathlib import Path
import pandas as pd

project = Path.cwd()

files = [
    project / "outputs" / "hsr_resource_norms.csv",
    project / "data" / "templates" / "hsr_activity_mapping.csv"
]

for path in files:
    print(f"\n=== {path.name} ===")

    if not path.exists():
        print("FILE NOT FOUND")
        continue

    df = pd.read_csv(path)
    print("Columns:", df.columns.tolist())
    print(df.to_string(index=False))

print("\nNo mappings changed and no resource estimates calculated.")
