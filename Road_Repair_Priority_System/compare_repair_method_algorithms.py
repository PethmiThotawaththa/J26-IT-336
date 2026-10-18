
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


# --------------------------------------------------
# 1. Paths and configuration
# --------------------------------------------------

DATA_PATH = Path("outputs/ml_cost_dataset.csv")
OUTPUT_PATH = Path(
    "outputs/repair_method_algorithm_comparison.csv"
)

FEATURES = [
    "Length (m)",
    "Width (m)",
    "Depth (m)",
    "Area (sqm)",
    "Count",
]

REPAIR_METHODS = {
    1: "Pothole Patching",
    2: "Crack Sealing",
    75: "Section Overlay",
}

LABELS = sorted(REPAIR_METHODS)


# --------------------------------------------------
# 2. Load and prepare RDA data
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

df["Item Code"] = pd.to_numeric(
    df["Item Code"], errors="coerce"
)

df = df[
    df["Item Code"].isin(LABELS)
].copy()

df = df.dropna(
    subset=["RoadID", "Item Code"]
).reset_index(drop=True)

for feature in FEATURES:
    df[feature] = pd.to_numeric(
        df[feature], errors="coerce"
    ).fillna(0)

df["Item Code"] = df["Item Code"].astype(int)

X = df[FEATURES]
y = df["Item Code"]
groups = df["RoadID"]

print("=" * 65)
print("REPAIR METHOD ML ALGORITHM COMPARISON")
print("=" * 65)

print(f"\nTotal records: {len(df)}")
print(f"Total roads: {groups.nunique()}")
print("\nClass distribution:")
print(y.value_counts().sort_index())

if groups.nunique() < 2:
    raise ValueError(
        "At least two roads are required for validation."
    )


# --------------------------------------------------
# 3. Define ML algorithms
# --------------------------------------------------

def get_algorithms():
    return {
        "Decision Tree": DecisionTreeClassifier(
            random_state=42,
            class_weight="balanced",
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        ),

        "Extra Trees": ExtraTreesClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        ),

        "Gradient Boosting": GradientBoostingClassifier(
            random_state=42,
        ),

        "KNN": make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(
                n_neighbors=3,
            ),
        ),

        "Logistic Regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    }


# --------------------------------------------------
# 4. Leave-One-Road-Out validation
# --------------------------------------------------

logo = LeaveOneGroupOut()

results = []

for name in get_algorithms():

    predictions = np.full(
        len(df), -1, dtype=int
    )

    valid = True

    for train_idx, test_idx in logo.split(
        X, y, groups
    ):

        X_train = X.iloc[train_idx]
        y_train = y.iloc[train_idx]
        X_test = X.iloc[test_idx]

        if y_train.nunique() < 2:
            print(
                f"\n{name}: skipped because a "
                "training fold has only one class."
            )
            valid = False
            break

        model = get_algorithms()[name]

        try:
            model.fit(X_train, y_train)
            predictions[test_idx] = model.predict(
                X_test
            )
        except ValueError as error:
            print(f"\n{name}: skipped - {error}")
            valid = False
            break

    if not valid:
        continue

    accuracy = accuracy_score(
        y, predictions
    )

    macro_f1 = f1_score(
        y,
        predictions,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y,
        predictions,
        labels=LABELS,
        average="weighted",
        zero_division=0,
    )

    results.append({
        "Algorithm": name,
        "Accuracy": accuracy,
        "Macro_F1": macro_f1,
        "Weighted_F1": weighted_f1,
        "Correct_Predictions": int(
            (y.to_numpy() == predictions).sum()
        ),
        "Total_Records": len(df),
    })

    print("\n" + "=" * 65)
    print(name.upper())
    print("=" * 65)

    print(f"Accuracy: {accuracy:.2%}")
    print(f"Macro F1: {macro_f1:.4f}")
    print(f"Weighted F1: {weighted_f1:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y,
            predictions,
            labels=LABELS,
            target_names=[
                REPAIR_METHODS[code]
                for code in LABELS
            ],
            zero_division=0,
        )
    )

    print("Confusion Matrix:")
    print(
        confusion_matrix(
            y,
            predictions,
            labels=LABELS,
        )
    )


# --------------------------------------------------
# 5. Compare results
# --------------------------------------------------

if not results:
    raise RuntimeError(
        "No algorithm completed validation."
    )

comparison = pd.DataFrame(results)

comparison = comparison.sort_values(
    by=["Macro_F1", "Accuracy"],
    ascending=False,
).reset_index(drop=True)

print("\n" + "=" * 65)
print("FINAL ALGORITHM COMPARISON")
print("=" * 65)

print(
    comparison.to_string(
        index=False,
        float_format=lambda value: f"{value:.4f}",
    )
)

comparison.to_csv(
    OUTPUT_PATH,
    index=False,
)

best = comparison.iloc[0]

print("\nHighest-ranked algorithm (by Macro F1):")
print(best["Algorithm"])
print(f"Accuracy: {best['Accuracy']:.2%}")
print(f"Macro F1: {best['Macro_F1']:.4f}")

print("\nComparison saved to:", OUTPUT_PATH)
print("\nCOMPARISON COMPLETE")
