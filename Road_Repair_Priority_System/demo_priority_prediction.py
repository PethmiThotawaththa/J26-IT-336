
from pathlib import Path
from datetime import datetime

import joblib
import numpy as np
import pandas as pd


# ============================================================
# ROAD REPAIR PRIORITY PREDICTION SYSTEM
# PROFESSIONAL INTERACTIVE DEMO
#
# 1. Predict an existing road section
# 2. Predict using manual inputs
# 3. Exit
#
# Uses the existing trained model.
# No training or model modification.
# ============================================================


MODEL_PATH = Path(
    "models/experimental_priority_classifier.joblib"
)

DATA_PATH = Path(
    "outputs/priority_ml_dataset_experimental.csv"
)

FEATURES = [
    "section_length_m",
    "traffic_mean_vehicles_per_hour",
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "section_forecast_budget_lkr",
    "planned_item_1_count",
    "planned_item_2_count",
    "planned_item_75_count",
]

FEATURE_LABELS = {
    "section_length_m": "Road section length (m)",
    "traffic_mean_vehicles_per_hour": "Mean traffic (vehicles/hour)",
    "nearby_hospital_count_500m": "Nearby hospitals within 500m",
    "nearby_school_count_500m": "Nearby schools within 500m",
    "nearby_police_count_500m": "Nearby police stations within 500m",
    "section_forecast_budget_lkr": "Forecast maintenance budget (LKR)",
    "planned_item_1_count": "Planned pothole patching items",
    "planned_item_2_count": "Planned crack sealing items",
    "planned_item_75_count": "Planned section overlay items",
}

COUNT_FEATURES = {
    "nearby_hospital_count_500m",
    "nearby_school_count_500m",
    "nearby_police_count_500m",
    "planned_item_1_count",
    "planned_item_2_count",
    "planned_item_75_count",
}

PRIORITY_DESCRIPTIONS = {
    "High": "Higher provisional maintenance / inspection priority.",
    "Medium": "Moderate provisional maintenance / inspection priority.",
    "Low": "Lower provisional maintenance / inspection priority.",
}


def separator(character="=", width=72):
    print(character * width)


def heading(text):
    print()
    separator()
    print(text.center(72))
    separator()


def section_heading(text):
    print()
    separator("-")
    print(text)
    separator("-")


def format_value(feature, value):
    if feature in COUNT_FEATURES:
        return str(int(value))

    if feature == "section_forecast_budget_lkr":
        return f"Rs. {float(value):,.2f}"

    return f"{float(value):,.2f}"


def read_number(feature):
    label = FEATURE_LABELS[feature]

    while True:
        raw = input(f"{label}: ").strip()

        try:
            value = float(raw.replace(",", ""))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if not np.isfinite(value):
            print("Please enter a finite number.")
            continue

        if feature == "section_length_m" and value <= 0:
            print("Section length must be greater than zero.")
            continue

        if feature != "section_length_m" and value < 0:
            print("Negative values are not allowed.")
            continue

        if feature in COUNT_FEATURES:
            if not value.is_integer():
                print("Please enter a whole-number count.")
                continue

            return int(value)

        return float(value)


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    # Load only the model created by this project.
    package = joblib.load(MODEL_PATH)

    if not isinstance(package, dict):
        raise ValueError("Invalid model package.")

    for key in ("model", "feature_columns", "target_name"):
        if key not in package:
            raise ValueError(
                f"Missing model information: {key}"
            )

    if list(package["feature_columns"]) != FEATURES:
        raise ValueError(
            "Model features do not match the demo inputs."
        )

    if package["target_name"] != (
        "provisional_maintenance_inspection_priority"
    ):
        raise ValueError("Unexpected model target.")

    model = package["model"]

    if model.n_features_in_ != len(FEATURES):
        raise ValueError("Model input count mismatch.")

    return model


def load_existing_data():
    if not DATA_PATH.exists():
        return None

    df = pd.read_csv(
        DATA_PATH,
        dtype={
            "section_id": "string",
            "road_id": "string",
        },
    )

    required = ["section_id", "road_id"] + FEATURES

    if any(column not in df.columns for column in required):
        return None

    if df.empty:
        return None

    if df["section_id"].isna().any():
        return None

    if df["section_id"].duplicated().any():
        return None

    for feature in FEATURES:
        df[feature] = pd.to_numeric(
            df[feature],
            errors="raise",
        )

    values = df[FEATURES].to_numpy(dtype=float)

    if not np.isfinite(values).all():
        return None

    return df.sort_values(
        ["road_id", "section_id"]
    ).reset_index(drop=True)


def display_inputs(values):
    section_heading("ROAD SECTION DETAILS")

    for number, feature in enumerate(FEATURES, start=1):
        label = FEATURE_LABELS[feature]
        value = format_value(feature, values[feature])

        print(f"{number:2}. {label:<42} {value}")


def predict_and_display(
    model,
    values,
    section_id,
    input_source,
    existing_data=None,
):
    input_df = pd.DataFrame(
        [values],
        columns=FEATURES,
    )

    prediction = str(model.predict(input_df)[0])

    if prediction not in {"High", "Medium", "Low"}:
        raise ValueError("Unexpected prediction result.")

    heading("ROAD PRIORITY PREDICTION RESULT")

    print(
        "Date:",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    print("Road Section:", section_id or "Not specified")
    print("Input Source:", input_source)

    section_heading("PREDICTED PRIORITY")

    print()
    print("  " + "*" * 40)
    print(f"       {prediction.upper()} PRIORITY")
    print("  " + "*" * 40)

    print()
    print(PRIORITY_DESCRIPTIONS[prediction])

    display_inputs(values)

    # Warn only when a manual scenario reuses an existing ID
    # with different feature values.
    if (
        input_source == "Manual input"
        and existing_data is not None
        and section_id
    ):
        matching = existing_data[
            existing_data["section_id"] == section_id
        ]

        if not matching.empty:
            original = matching.iloc[0]

            same_values = all(
                np.isclose(
                    float(values[feature]),
                    float(original[feature]),
                    rtol=1e-9,
                    atol=1e-8,
                )
                for feature in FEATURES
            )

            if not same_values:
                print()
                print(
                    "Note: Entered values differ from the "
                    "saved data for this section ID."
                )

    return prediction


def predict_existing(model, existing_data):
    heading("EXISTING ROAD SECTION PREDICTION")

    if existing_data is None:
        print("Existing road section data is unavailable.")
        return

    print("\nAvailable road sections:\n")

    for index, row in existing_data.iterrows():
        print(f"{index + 1:2}. {row['section_id']}")

    print("\n0. Back to main menu")

    while True:
        raw = input(
            "\nSelect section number or section ID: "
        ).strip()

        if raw == "0":
            return

        selected_row = None

        # Allow either a number or a section ID.
        if raw.isdigit():
            index = int(raw) - 1

            if 0 <= index < len(existing_data):
                selected_row = existing_data.iloc[index]

        if selected_row is None:
            matching = existing_data[
                existing_data["section_id"].str.upper()
                == raw.upper()
            ]

            if not matching.empty:
                selected_row = matching.iloc[0]

        if selected_row is not None:
            break

        print("Invalid selection. Please try again.")

    section_id = str(selected_row["section_id"])

    values = {
        feature: float(selected_row[feature])
        for feature in FEATURES
    }

    predict_and_display(
        model=model,
        values=values,
        section_id=section_id,
        input_source="Existing project data",
        existing_data=existing_data,
    )


def predict_manual(model, existing_data):
    heading("MANUAL ROAD SECTION PREDICTION")

    print("\nEnter the road section information below.\n")

    section_id = input(
        "Road section ID (optional): "
    ).strip()

    values = {}

    section_heading("ENTER ROAD SECTION DETAILS")

    for index, feature in enumerate(FEATURES, start=1):
        print(f"\nInput {index}/{len(FEATURES)}")
        values[feature] = read_number(feature)

    section_heading("CONFIRM INPUT DETAILS")

    display_inputs(values)

    while True:
        confirmation = input(
            "\nGenerate prediction? (y/n): "
        ).strip().lower()

        if confirmation in {"y", "yes", "n", "no"}:
            break

        print("Please enter y or n.")

    if confirmation in {"n", "no"}:
        print("\nPrediction cancelled.")
        return

    predict_and_display(
        model=model,
        values=values,
        section_id=section_id,
        input_source="Manual input",
        existing_data=existing_data,
    )


def main():
    heading("ROAD REPAIR PRIORITY DECISION SUPPORT SYSTEM")

    print("Component: Road Priority Prediction")
    print("Prediction Classes: High / Medium / Low")

    model = load_model()
    existing_data = load_existing_data()

    print("\nPriority prediction model loaded successfully.")

    while True:
        heading("MAIN MENU")

        print("1. Predict an existing road section")
        print("2. Predict using manually entered inputs")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            predict_existing(model, existing_data)
            input("\nPress ENTER to return to the main menu...")

        elif choice == "2":
            predict_manual(model, existing_data)
            input("\nPress ENTER to return to the main menu...")

        elif choice == "3":
            heading("PROGRAM CLOSED")
            print("Thank you for using the system.")
            break

        else:
            print("\nInvalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram stopped by user.")
    except (FileNotFoundError, ValueError) as error:
        print(f"\nError: {error}")
        raise SystemExit(1)
