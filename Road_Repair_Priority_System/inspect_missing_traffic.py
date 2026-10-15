
import pandas as pd
from pathlib import Path

project = Path(__file__).parent

file_path = project / "outputs" / "cleaned_traffic.csv"

df = pd.read_csv(file_path)

# Road ID missing වෙලා තියෙන rows
missing_rows = df[df["ROUTE NO"].isna()]

print("MISSING TRAFFIC RECORDS")
print("=======================")

print("Total missing Road IDs:", len(missing_rows))

print("\nAll rows with missing Road IDs:")
print(missing_rows.to_string(index=True))

print("\nINSPECTION COMPLETED!")
