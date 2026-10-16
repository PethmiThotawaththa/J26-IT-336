
from pathlib import Path

import pandas as pd


# Define project paths
project = Path(__file__).parent

data_file = project / "outputs" / "ml_cost_dataset.csv"

predictions_file = (
    project / "outputs" / "road_validation_predictions.csv"
)

output_file = (
    project / "outputs" / "item_code_coverage.csv"
)


# Load the original dataset and validation predictions
df = pd.read_csv(data_file)
predictions = pd.read_csv(predictions_file)


# Check required columns
required_data_columns = [
    "RoadID",
    "Item Code"
]

required_prediction_columns = [
    "RoadID",
    "Item Code",
    "RF_Absolute_Error_LKR"
]

for column in required_data_columns:
    if column not in df.columns:
        raise ValueError(
            f"Missing column in ML dataset: {column}"
        )

for column in required_prediction_columns:
    if column not in predictions.columns:
        raise ValueError(
            f"Missing column in predictions: {column}"
        )


# Standardize road IDs and item codes
df["RoadID"] = df["RoadID"].astype(str)
df["Item Code"] = df["Item Code"].astype(str)

predictions["RoadID"] = (
    predictions["RoadID"].astype(str)
)

predictions["Item Code"] = (
    predictions["Item Code"].astype(str)
)


# Verify that validation predictions cover the dataset
if len(predictions) != len(df):
    raise ValueError(
        "Prediction record count does not match the dataset."
    )


# Calculate item code coverage for each held-out road
coverage_records = []

roads = sorted(df["RoadID"].unique())

for test_road in roads:

    # Separate the held-out road and training roads
    train_data = df[df["RoadID"] != test_road]
    test_data = df[df["RoadID"] == test_road]

    test_predictions = predictions[
        predictions["RoadID"] == test_road
    ]

    # Count training examples for every item code
    train_item_counts = (
        train_data["Item Code"].value_counts()
    )

    # Count testing examples for every item code
    test_item_counts = (
        test_data["Item Code"].value_counts()
    )

    for item_code, test_count in test_item_counts.items():

        train_count = int(
            train_item_counts.get(item_code, 0)
        )

        # Find the mean prediction error for this item
        item_predictions = test_predictions[
            test_predictions["Item Code"] == item_code
        ]

        item_mae = (
            item_predictions["RF_Absolute_Error_LKR"]
            .mean()
        )

        coverage_records.append({
            "Test_Road": test_road,
            "Item_Code": item_code,
            "Training_Examples": train_count,
            "Testing_Examples": int(test_count),
            "Item_MAE_LKR": item_mae
        })


# Create the coverage report
coverage = pd.DataFrame(coverage_records)


# Label the amount of available training data
def classify_coverage(count):

    if count == 0:
        return "Unseen"

    if count <= 2:
        return "Very Low"

    if count <= 5:
        return "Low"

    return "Higher"


coverage["Coverage_Level"] = (
    coverage["Training_Examples"]
    .apply(classify_coverage)
)


# Display overall dataset information
print("ITEM CODE TRAINING COVERAGE ANALYSIS")
print("===================================")

print("Total repair records:", len(df))
print("Total roads:", df["RoadID"].nunique())
print("Total item codes:", df["Item Code"].nunique())


# Display coverage summary
print("\nTRAINING COVERAGE SUMMARY")
print("=========================")

print(
    coverage["Coverage_Level"]
    .value_counts()
    .to_string()
)


# Display cases with no training examples
print("\nUNSEEN ITEM CODES IN HELD-OUT ROADS")
print("===================================")

unseen = coverage[
    coverage["Training_Examples"] == 0
]

if unseen.empty:
    print("No unseen item codes found.")
else:
    print(
        unseen[
            [
                "Test_Road",
                "Item_Code",
                "Testing_Examples",
                "Item_MAE_LKR"
            ]
        ].to_string(index=False)
    )


# Display coverage specifically for Item Code 69
print("\nITEM CODE 69 COVERAGE")
print("=====================")

item_69 = coverage[
    coverage["Item_Code"] == "69"
]

if item_69.empty:
    print("Item Code 69 was not found.")
else:
    print(
        item_69[
            [
                "Test_Road",
                "Training_Examples",
                "Testing_Examples",
                "Item_MAE_LKR",
                "Coverage_Level"
            ]
        ].to_string(index=False)
    )


# Display high-error cases and their coverage
print("\nTOP 15 ITEM-ROAD COMBINATIONS BY ERROR")
print("======================================")

top_errors = coverage.nlargest(
    15,
    "Item_MAE_LKR"
)

print(
    top_errors[
        [
            "Test_Road",
            "Item_Code",
            "Training_Examples",
            "Testing_Examples",
            "Item_MAE_LKR",
            "Coverage_Level"
        ]
    ].to_string(index=False)
)


# Save the complete coverage analysis
coverage.to_csv(
    output_file,
    index=False
)

print("\nSaved coverage report:", output_file)
print("\nITEM CODE COVERAGE ANALYSIS COMPLETED!")
