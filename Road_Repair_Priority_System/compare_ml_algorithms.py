
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Define project paths
project = Path(__file__).parent

data_file = project / "outputs" / "ml_cost_dataset.csv"

output_file = (
    project / "outputs" / "ml_algorithm_comparison.csv"
)


# Load historical repair data
df = pd.read_csv(data_file)


# Create an engineering input feature
df["Calculated_Work_Area_sqm"] = (
    df["Length (m)"] * df["Width (m)"]
)


# Define numerical input features
numeric_features = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)",
    "Calculated_Work_Area_sqm"
]


# Define categorical input features
categorical_features = [
    "RoadID",
    "Item Code",
    "Units"
]


# Prepare input features and target
feature_columns = numeric_features + categorical_features

X = df[feature_columns].copy()
y = df["Repair_Cost_LKR"]

groups = df["RoadID"].astype(str)

for column in categorical_features:
    X[column] = X[column].astype(str)


# Define the machine learning algorithms
algorithms = {
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),

    "Extra Trees": ExtraTreesRegressor(
        n_estimators=200,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
}


# Use the same road-based validation for every model
logo = LeaveOneGroupOut()

all_predictions = {}


print("ML ALGORITHM COMPARISON")
print("=======================")

print("Total records:", len(df))
print("Total roads:", groups.nunique())
print("Validation: Leave-One-Road-Out")


# Train and evaluate each machine learning algorithm
for name, regressor in algorithms.items():

    # Encode categories using training data within each fold
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                "passthrough",
                numeric_features
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            )
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", regressor)
        ]
    )

    predictions = np.zeros(len(df))

    # Hold out one road at a time
    for train_idx, test_idx in logo.split(X, y, groups):

        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]

        y_train = y.iloc[train_idx]

        # Fit the model on the other roads only
        model.fit(X_train, y_train)

        # Predict costs for the unseen road
        predictions[test_idx] = model.predict(X_test)

    # Calculate overall prediction errors
    mae = mean_absolute_error(y, predictions)

    rmse = np.sqrt(
        mean_squared_error(y, predictions)
    )

    r2 = r2_score(y, predictions)

    print(f"\nMODEL: {name}")
    print(f"MAE (LKR): {mae:.2f}")
    print(f"RMSE (LKR): {rmse:.2f}")
    print(f"R2 Score: {r2:.4f}")

    all_predictions[name] = predictions


# Save predictions for further analysis
results = pd.DataFrame({
    "RoadID": df["RoadID"],
    "Item_Code": df["Item Code"],
    "Actual_Cost_LKR": y,
    "Random_Forest_Predicted_LKR": (
        all_predictions["Random Forest"]
    ),
    "Extra_Trees_Predicted_LKR": (
        all_predictions["Extra Trees"]
    ),
    "Gradient_Boosting_Predicted_LKR": (
        all_predictions["Gradient Boosting"]
    )
})

results.to_csv(output_file, index=False)

print("\nSaved comparison:", output_file)
print("\nML ALGORITHM COMPARISON COMPLETED!")
