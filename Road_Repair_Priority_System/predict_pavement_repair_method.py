
from pathlib import Path

import joblib
import pandas as pd


# -----------------------------------------------
# 1. Load trained repair method ML model
# -----------------------------------------------

MODEL_PATH = Path(
    "models/experimental_pavement_repair_model.joblib"
)

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}\n"
        "Please run train_pavement_repair_model.py first."
    )

model_package = joblib.load(MODEL_PATH)

model = model_package["model"]
features = model_package["features"]
repair_methods = model_package["repair_methods"]


# -----------------------------------------------
# 2. Collect input measurements
# -----------------------------------------------

print("=" * 55)
print("ROAD REPAIR METHOD PREDICTION")
print("=" * 55)

print("\nEnter the measurement values below.\n")

input_values = {}

for feature in features:
    while True:
        try:
            value = float(input(f"{feature}: "))

            if value < 0:
                print(
                    "Please enter a non-negative value."
                )
                continue

            input_values[feature] = value
            break

        except ValueError:
            print("Please enter a valid number.")


# -----------------------------------------------
# 3. Predict repair method using ML
# -----------------------------------------------

input_df = pd.DataFrame(
    [input_values],
    columns=features,
)

predicted_code = int(
    model.predict(input_df)[0]
)

predicted_method = repair_methods.get(
    predicted_code,
    "Unknown Repair Method",
)


# -----------------------------------------------
# 4. Display prediction
# -----------------------------------------------

print("\n" + "=" * 55)
print("REPAIR METHOD PREDICTION RESULT")
print("=" * 55)

print(f"\nPredicted RDA Code: {predicted_code}")
print(f"Predicted Repair Method: {predicted_method}")

print("\nInput measurements:")

for feature, value in input_values.items():
    print(f"  {feature}: {value}")

print("\nPrediction completed.")
