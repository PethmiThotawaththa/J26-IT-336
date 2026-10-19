from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "data/templates/maintenance_tasks.csv",
    ROOT / "data/templates/task_requirements.csv",
    ROOT / "data/templates/resource_availability.csv",
    ROOT / "data/templates/source_register.csv",
]

def main():
    for path in FILES:
        print(f"\n--- {path.relative_to(ROOT)} ---")
        df = pd.read_csv(path)
        print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
        print("Columns:", ", ".join(df.columns))
        if df.empty:
            print("Template is empty: add authorized, cleaned data before using it.")
        else:
            print("\nMissing values:")
            print(df.isna().sum().to_string())
            print("\nPreview:")
            print(df.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
