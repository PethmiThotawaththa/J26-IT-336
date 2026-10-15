
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).parent
data_folder = project_folder / "datasets"

# Traffic Excel file එක automatically හොයනවා
excel_files = list(data_folder.glob("*.xlsx"))

traffic_files = [
    file for file in excel_files
    if "traffic" in file.name.lower()
]

if not traffic_files:
    print("ERROR: Traffic Excel file not found!")

else:
    traffic_file = traffic_files[0]

    print("TRAFFIC DATASET ANALYSIS")
    print("========================")
    print("File:", traffic_file.name)

    # Excel workbook එකේ sheets හොයනවා
    workbook = pd.ExcelFile(traffic_file)

    print("\nSheet Names:")
    print(workbook.sheet_names)

    # හැම sheet එකක්ම inspect කරනවා
    for sheet in workbook.sheet_names:

        df = pd.read_excel(
            traffic_file,
            sheet_name=sheet
        )

        print("\n------------------------")
        print("SHEET:", sheet)
        print("Rows:", len(df))
        print("Columns:", len(df.columns))

        print("\nColumn Names:")
        print(df.columns.tolist())

        print("\nFirst 5 Rows:")
        print(df.head(5).to_string(index=False))

    print("\nTRAFFIC ANALYSIS COMPLETED!")
