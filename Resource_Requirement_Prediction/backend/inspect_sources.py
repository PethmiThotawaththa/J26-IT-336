from pathlib import Path
import pandas as pd

root = Path(r"D:\Y4S1\RP\PP1\RESOURCES")

workbooks = [
    root / "Forecasted routine maintenance budget 2026.xlsx",
    root / "RDA" / "Traffic Data of Roads (B047, B174, B214, B240, B263 and B435).xlsx",
]

for path in workbooks:
    print("\n" + "=" * 80)
    print("WORKBOOK:", path.name)

    if not path.exists():
        print("FILE NOT FOUND")
        continue

    excel = pd.ExcelFile(path)
    print("SHEETS:", excel.sheet_names)

    for sheet in excel.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        print(f"\nSHEET: {sheet} | ROWS: {len(df)} | COLUMNS: {len(df.columns)}")
        print("COLUMN NAMES:", df.columns.tolist())
        print(df.head(3).to_string(index=False))

weather_path = root / "Whether.csv"
print("\n" + "=" * 80)
print("WEATHER FILE:", weather_path.name)

if weather_path.exists():
    weather = pd.read_csv(weather_path)
    print("ROWS:", len(weather))
    print("COLUMNS:", weather.columns.tolist())
    print("\nDATA TYPES:")
    print(weather.dtypes.to_string())
    print("\nFIRST 5 ROWS:")
    print(weather.head().to_string(index=False))
else:
    print("FILE NOT FOUND")
