
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error


# Define project paths
project = Path(__file__).parent

input_file = (
    project / "outputs" / "ml_algorithm_comparison.csv"
)

output_file = (
    project / "outputs" / "algorithm_road_analysis.csv"
)


# Load the saved ML validation predictions
df = pd.read_csv(input_file)


# Define the prediction columns
models = {
    "Random Forest": "Random_Forest_Predicted_LKR",
    "Extra Trees": "Extra_Trees_Predicted_LKR",
    "Gradient Boosting": "Gradient_Boosting_Predicted_LKR"
}


# Calculate MAE for each road and each model
results = []

for road_id, road_df in df.groupby("RoadID"):

    actual = road_df["Actual_Cost_LKR"]

    row = {
        "RoadID": road_id,
        "Records": len(road_df)
    }

    for model_name, prediction_column in models.items():

        mae = mean_absolute_error(
            actual,
            road_df[prediction_column]
        )

        row[model_name + "_MAE_LKR"] = mae

    # Find the model with the lowest MAE on this road
    road_errors = {
        model_name: row[model_name + "_MAE_LKR"]
        for model_name in models
    }

    row["Lowest_MAE_Model"] = min(
        road_errors,
        key=road_errors.get
    )

    results.append(row)


# Convert the results to a DataFrame
results_df = pd.DataFrame(results)


# Display road-by-road results
print("ROAD-BY-ROAD ML ALGORITHM ANALYSIS")
print("==================================")

print("\nMAE BY ROAD (LKR)")
print("=================")

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:,.2f}"
    )
)


# Count how many roads each model performs best on
print("\nNUMBER OF ROADS WITH LOWEST MAE")
print("================================")

for model_name in models:

    count = (
        results_df["Lowest_MAE_Model"] == model_name
    ).sum()

    print(f"{model_name}: {count}")


# Calculate overall MAE again for reference
print("\nOVERALL MAE ACROSS ALL RECORDS")
print("==============================")

for model_name, prediction_column in models.items():

    mae = mean_absolute_error(
        df["Actual_Cost_LKR"],
        df[prediction_column]
    )

    print(f"{model_name}: Rs. {mae:,.2f}")


# Save the road-level comparison
results_df.to_csv(
    output_file,
    index=False
)

print("\nSaved analysis:", output_file)
print("\nROAD-LEVEL ANALYSIS COMPLETED!")
