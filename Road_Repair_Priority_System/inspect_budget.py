
import pandas as pd
from pathlib import Path

project = Path(__file__).parent
data_folder = project / "datasets"

# Find budget Excel files
excel_files = list(data_folder.glob("*.xlsx"))

budget_files = [
    f for f in excel_files
    if "forecast" in f.name.lower()
    or "budget" in f.name.lower()
]

if not budget_files:
    print("ERROR: Budget Excel file not found!")

else:
    budget_file = budget_files[0]

    print("MAINTENANCE BUDGET ANALYSIS")
    print("===========================")
    print("File:", budget_file.name)

    workbook = pd.ExcelFile(budget_file)

    print("\nSheet Names:")
    print(workbook.sheet_names)

    for sheet in workbook.sheet_names:

        df = pd.read_excel(
            budget_file,
            sheet_name=sheet
        )

        print("\n------------------------")
        print("SHEET:", sheet)
        print("Rows:", len(df))
        print("Columns:", len(df.columns))

        print("\nColumn Names:")
        print(df.columns.tolist())

        print("\nFirst 10 Rows:")
        print(df.head(10).to_string(index=False))

    print("\nBUDGET ANALYSIS COMPLETED!")
