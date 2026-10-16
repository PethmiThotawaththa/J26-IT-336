
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Define project paths
project = Path(__file__).parent
data_file = project / "outputs" / "ml_cost_dataset.csv"
results_file = project / "outputs" / "cost_baseline_predictions.csv"


# Load the prepared ML dataset
df = pd.read_csv(data_file)


# Select numerical input features
numeric_features = [
    "StartChainage(m)",
    "EndChainage(m)",
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
    "Times per year (Frequency)",
    "Density (kg/m3)"
]


# Select categorical input features
categorical_features = [
    "RoadID",
    "Item Code",
    "Units"
]


# Separate input features (X) and target (y)
feature_columns = numeric_features + categorical_features

X = df[feature_columns].copy()
y = df["Repair_Cost_LKR"]


# Treat item codes and road IDs as categories
for column in categorical_features:
    X[column] = X[column].astype(str)


# Split records into training and testing datasets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


# Convert categorical features into numerical form
preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", "passthrough", numeric_features),
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ]
)


# Create the Random Forest prediction pipeline
random_forest = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestRegressor(
                n_estimators=200,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)


# Create a simple comparison model
dummy_model = DummyRegressor(strategy="median")


# Train both models using training records only
dummy_model.fit(X_train, y_train)
random_forest.fit(X_train, y_train)


# Evaluate predictions against unseen test records
def evaluate_model(name, model):
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    print(f"\nMODEL: {name}")
    print(f"MAE (LKR): {mae:.2f}")
    print(f"RMSE (LKR): {rmse:.2f}")
    print(f"R2 Score: {r2:.4f}")

    return predictions


# Print experiment details
print("ML COST BASELINE EXPERIMENT")
print("===========================")
print("Total records:", len(df))
print("Training records:", len(X_train))
print("Testing records:", len(X_test))


# Evaluate the comparison model and Random Forest
evaluate_model("Dummy Median Baseline", dummy_model)

rf_predictions = evaluate_model(
    "Random Forest Regressor",
    random_forest
)


# Save actual and predicted repair costs
results = X_test.copy()
results["Actual_Cost_LKR"] = y_test.values
results["Predicted_Cost_LKR"] = rf_predictions

results["Absolute_Error_LKR"] = abs(
    results["Actual_Cost_LKR"]
    - results["Predicted_Cost_LKR"]
)

results.to_csv(results_file, index=False)


# Display output information
print("\nSaved predictions:", results_file)
print("\nBASELINE EXPERIMENT COMPLETED!")
