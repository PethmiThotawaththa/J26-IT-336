from pathlib import Path
import pandas as pd

path = Path(
    r"D:\Y4S1\RP\PP1\RESOURCES\RDA"
    r"\Traffic Data of Roads (B047, B174, B214, B240, B263 and B435).xlsx"
)

df = pd.read_excel(path, sheet_name="Traffic Counts")
df.insert(0, "Excel_Row", range(2, len(df) + 2))

def normalize_road_id(value):
    if pd.isna(value):
        return None
    value = str(value).strip().upper()
    if value.startswith("B") and value[1:].isdigit():
        return "B" + value[1:].lstrip("0").zfill(3)
    return value

df["Normalized_RoadID"] = df["ROUTE NO"].apply(normalize_road_id)

print("=== ALL TRAFFIC WORKSHEET ROWS ===")
print(
    df[[
        "Excel_Row", "ROUTE NO", "Normalized_RoadID",
        "NAME OF ROAD", "Chainage (KM)",
        "DATE OF COUNT", "TOTAL NO.OF VEH.", "HRS OF COUNT"
    ]].to_string(index=False)
)

print("\n=== ROW CLASSIFICATION ===")
valid = df["ROUTE NO"].notna() & df["DATE OF COUNT"].notna()
print("Rows with route and date:", int(valid.sum()))
print("Rows missing route or date:", int((~valid).sum()))

print("\n=== RAW DATE VALUES ===")
for row_num, value in zip(df["Excel_Row"], df["DATE OF COUNT"]):
    print(f"Excel row {row_num}: {value!r}")
