
from pathlib import Path
from datetime import datetime
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

MODEL_FILES = [
    "experimental_pavement_repair_model.joblib",
    "experimental_priority_classifier.joblib",
    "final_extra_trees_cost_model.joblib",
    "repair_cost_model.joblib",
    "repair_cost_model_without_road_id.joblib",
]


def print_value(name, value):
    print(f"\n{name}:")
    print(value)


def inspect_model(filename):
    print("\n" + "=" * 75)
    print("MODEL FILE:", filename)
    print("=" * 75)

    model_path = MODELS_DIR / filename

    if not model_path.exists():
        print("STATUS: FILE NOT FOUND")
        return

    file_info = model_path.stat()

    print("File size (bytes):", file_info.st_size)
    print(
        "Last modified:",
        datetime.fromtimestamp(file_info.st_mtime).isoformat(
            sep=" ", timespec="seconds"
        ),
    )

    try:
        saved_object = joblib.load(model_path)
    except Exception as error:
        print("MODEL LOAD ERROR:", repr(error))
        return

    print("Saved object type:", type(saved_object).__name__)

    if isinstance(saved_object, dict):
        print_value("Package keys", list(saved_object.keys()))

        metadata_keys = [
            "feature_columns",
            "feature_names",
            "input_columns",
            "numeric_columns",
            "categorical_columns",
            "target_name",
            "model_name",
            "algorithm",
            "created_utc",
            "training_roads",
            "training_sections",
            "evaluation_note",
        ]

        for key in metadata_keys:
            if key in saved_object:
                print_value(key, saved_object[key])

        model = None

        for key in ["model", "pipeline", "estimator"]:
            if key in saved_object:
                model = saved_object[key]
                print("\nEstimator package key:", key)
                break

        if model is None:
            print("\nNo recognized estimator key found.")
            return
    else:
        model = saved_object

    print("\nEstimator type:", type(model).__name__)
    print("Estimator module:", type(model).__module__)

    if hasattr(model, "feature_names_in_"):
        print_value(
            "Estimator input feature names",
            list(model.feature_names_in_),
        )

    if hasattr(model, "n_features_in_"):
        print(
            "\nNumber of input features:",
            model.n_features_in_,
        )

    if hasattr(model, "classes_"):
        print_value(
            "Prediction classes",
            list(model.classes_),
        )

    if hasattr(model, "named_steps"):
        print("\nPipeline steps:")

        for step_name, step in model.named_steps.items():
            print(
                f" - {step_name}: {type(step).__name__}"
            )

            if hasattr(step, "feature_names_in_"):
                print(
                    "   Input features:",
                    list(step.feature_names_in_),
                )

            if hasattr(step, "transformers"):
                print("   Transformers:")

                for transformer in step.transformers:
                    print(
                        "   ",
                        transformer[0],
                        "->",
                        transformer[2],
                    )


def main():
    print("=" * 75)
    print("EXISTING ML MODEL INSPECTION REPORT")
    print("=" * 75)

    print("Inspection mode: READ ONLY")
    print("Model training: NO")
    print("Model saving: NO")
    print("Model modification: NO")

    for filename in MODEL_FILES:
        inspect_model(filename)

    print("\n" + "=" * 75)
    print("INSPECTION COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()
