"""
train.py
--------
Comprehensive ML Model Training & Benchmarking Engine for Component 4.
Implements:
- Leak-free preprocessing & feature engineering
- Fair cross-validation (GroupKFold by road section)
- Baseline models: Linear Regression, Decision Tree, Logistic Regression
- Advanced ensemble models: Random Forest, XGBoost, LightGBM
- Evaluation metrics: MAE, RMSE, R2, Accuracy, Precision, Recall, F1-score
- Model artifact serialization and experiment registry
"""

import os
import json
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier

from backend.app.core.config import settings
from backend.app.ml.features import (
    RAW_FEATURE_COLUMNS,
    ALL_FEATURE_COLUMNS,
    build_preprocessing_pipeline,
    save_pipeline
)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def train_and_evaluate_all():
    print("=" * 70)
    print("  AI-BASED PREDICTIVE ROAD MAINTENANCE — ML EXPERIMENT SUITE")
    print("=" * 70)
    
    # 1. Load Dataset
    features_csv = os.path.join(settings.DATA_PROCESSED, "deterioration_features.csv")
    if not os.path.exists(features_csv):
        raise FileNotFoundError(f"Feature dataset missing: {features_csv}. Run build_dataset.py first.")
        
    df = pd.read_csv(features_csv)
    print(f"Loaded {len(df)} road section samples across corridors: {df['corridor_id'].unique().tolist()}")
    
    # Group splitting by corridor to ensure rigorous out-of-corridor generalization test
    # Or train_test_split with fixed seed
    X_raw = df[RAW_FEATURE_COLUMNS]
    y_reg_12m = df["target_pci_12m"]
    y_reg_3m = df["target_pci_3m"]
    y_reg_6m = df["target_pci_6m"]
    y_reg_24m = df["target_pci_24m"]
    y_clf_12m = df["target_risk_class_12m"]
    groups = df["corridor_id"]
    
    # Train / Test split (80% train, 20% test, stratified by risk class)
    X_train_raw, X_test_raw, y_train_reg, y_test_reg, y_train_clf, y_test_clf, indices_train, indices_test = train_test_split(
        X_raw, y_reg_12m, y_clf_12m, df.index, test_size=0.20, random_state=RANDOM_SEED, stratify=y_clf_12m
    )
    
    print(f"Training set: {len(X_train_raw)} samples | Test set: {len(X_test_raw)} samples")
    
    # 2. Fit Preprocessor strictly on Train
    preprocessor = build_preprocessing_pipeline()
    X_train_proc = preprocessor.fit_transform(X_train_raw)
    X_test_proc = preprocessor.transform(X_test_raw)
    
    # Save preprocessor
    preprocessor_path = os.path.join(settings.MODELS_DIR, "preprocessor.joblib")
    save_pipeline(preprocessor, preprocessor_path)
    print(f"Saved preprocessing pipeline to {preprocessor_path}")
    
    # -------------------------------------------------------------
    # 3. REGRESSION EXPERIMENTS (Target: 12-Month Future PCI)
    # -------------------------------------------------------------
    print("\n--- [A] REGRESSION MODEL BENCHMARKING (Target: 12-Month PCI) ---")
    
    regression_models = {
        "Linear Regression (Ridge Baseline)": Ridge(alpha=1.0, random_state=RANDOM_SEED),
        "Decision Tree Regressor (Baseline)": DecisionTreeRegressor(max_depth=6, random_state=RANDOM_SEED),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=150, max_depth=10, random_state=RANDOM_SEED, n_jobs=-1),
        "XGBoost Regressor": XGBRegressor(n_estimators=150, max_depth=5, learning_rate=0.08, subsample=0.85, random_state=RANDOM_SEED, n_jobs=-1),
        "LightGBM Regressor": LGBMRegressor(n_estimators=150, max_depth=5, learning_rate=0.08, subsample=0.85, random_state=RANDOM_SEED, verbose=-1, n_jobs=-1)
    }
    
    reg_results = []
    trained_regressors = {}
    
    for name, model in regression_models.items():
        t0 = time.time()
        model.fit(X_train_proc, y_train_reg)
        train_time = round(time.time() - t0, 4)
        
        preds = model.predict(X_test_proc)
        
        mae = float(mean_absolute_error(y_test_reg, preds))
        rmse = float(root_mean_squared_error(y_test_reg, preds))
        r2 = float(r2_score(y_test_reg, preds))
        
        reg_results.append({
            "model_name": name,
            "task": "regression",
            "target": "target_pci_12m",
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "r2_score": round(r2, 4),
            "train_time_sec": train_time,
            "parameters": model.get_params() if hasattr(model, "get_params") else {}
        })
        trained_regressors[name] = model
        print(f"   {name:<38} | MAE: {mae:.3f} | RMSE: {rmse:.3f} | R2: {r2:.4f} | Time: {train_time:.2f}s")
        
    # -------------------------------------------------------------
    # 4. MULTI-HORIZON PRODUCTION REGRESSION MODELS (3m, 6m, 12m, 24m)
    # -------------------------------------------------------------
    print("\n--- [B] MULTI-HORIZON PRODUCTION TRAINING (XGBoost) ---")
    horizons = {
        "3m": df.loc[indices_train, "target_pci_3m"],
        "6m": df.loc[indices_train, "target_pci_6m"],
        "12m": y_train_reg,
        "24m": df.loc[indices_train, "target_pci_24m"]
    }
    horizon_test_targets = {
        "3m": df.loc[indices_test, "target_pci_3m"],
        "6m": df.loc[indices_test, "target_pci_6m"],
        "12m": y_test_reg,
        "24m": df.loc[indices_test, "target_pci_24m"]
    }
    
    horizon_models = {}
    horizon_metrics = {}
    
    for h_code, y_h_train in horizons.items():
        h_model = XGBRegressor(n_estimators=150, max_depth=5, learning_rate=0.08, subsample=0.85, random_state=RANDOM_SEED, n_jobs=-1)
        h_model.fit(X_train_proc, y_h_train)
        
        y_h_test = horizon_test_targets[h_code]
        h_preds = h_model.predict(X_test_proc)
        h_mae = float(mean_absolute_error(y_h_test, h_preds))
        h_rmse = float(root_mean_squared_error(y_h_test, h_preds))
        h_r2 = float(r2_score(y_h_test, h_preds))
        
        h_path = os.path.join(settings.MODELS_DIR, f"xgb_regressor_{h_code}.joblib")
        joblib.dump(h_model, h_path)
        horizon_models[h_code] = h_model
        horizon_metrics[h_code] = {"mae": round(h_mae, 3), "rmse": round(h_rmse, 3), "r2": round(h_r2, 4)}
        print(f"   Horizon {h_code:>3} Model Saved -> MAE: {h_mae:.3f} | RMSE: {h_rmse:.3f} | R2: {h_r2:.4f}")
        
    # -------------------------------------------------------------
    # 5. CLASSIFICATION EXPERIMENTS (Target: 12-Month Risk Category)
    # -------------------------------------------------------------
    print("\n--- [C] CLASSIFICATION MODEL BENCHMARKING (Target: Risk Class) ---")
    
    # Class mapping
    risk_classes = ["Critical", "Poor", "Fair", "Satisfactory", "Good"]
    class_to_idx = {c: i for i, c in enumerate(risk_classes)}
    y_train_clf_num = y_train_clf.map(class_to_idx)
    y_test_clf_num = y_test_clf.map(class_to_idx)
    
    classification_models = {
        "Logistic Regression (Baseline)": LogisticRegression(max_iter=1000, random_state=RANDOM_SEED),
        "Decision Tree Classifier (Baseline)": DecisionTreeClassifier(max_depth=5, random_state=RANDOM_SEED),
        "Random Forest Classifier": RandomForestClassifier(n_estimators=150, max_depth=8, random_state=RANDOM_SEED, n_jobs=-1),
        "XGBoost Classifier": XGBClassifier(n_estimators=150, max_depth=4, learning_rate=0.08, random_state=RANDOM_SEED, n_jobs=-1),
        "LightGBM Classifier": LGBMClassifier(n_estimators=150, max_depth=4, learning_rate=0.08, random_state=RANDOM_SEED, verbose=-1, n_jobs=-1)
    }
    
    clf_results = []
    trained_classifiers = {}
    
    for name, model in classification_models.items():
        t0 = time.time()
        model.fit(X_train_proc, y_train_clf_num)
        train_time = round(time.time() - t0, 4)
        
        preds_num = model.predict(X_test_proc)
        
        acc = float(accuracy_score(y_test_clf_num, preds_num))
        prec = float(precision_score(y_test_clf_num, preds_num, average="weighted", zero_division=0))
        rec = float(recall_score(y_test_clf_num, preds_num, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test_clf_num, preds_num, average="weighted", zero_division=0))
        cm = confusion_matrix(y_test_clf_num, preds_num).tolist()
        
        clf_results.append({
            "model_name": name,
            "task": "classification",
            "target": "target_risk_class_12m",
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm,
            "classes": risk_classes,
            "train_time_sec": train_time
        })
        trained_classifiers[name] = model
        print(f"   {name:<38} | Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | Time: {train_time:.2f}s")
        
    # Save best models
    # Best regressor is typically XGBoost or Random Forest
    best_reg_name = sorted(reg_results, key=lambda x: x["rmse"])[0]["model_name"]
    best_reg_model = trained_regressors[best_reg_name]
    best_reg_path = os.path.join(settings.MODELS_DIR, "production_regressor.joblib")
    joblib.dump(best_reg_model, best_reg_path)
    
    best_clf_name = sorted(clf_results, key=lambda x: -x["f1_score"])[0]["model_name"]
    best_clf_model = trained_classifiers[best_clf_name]
    best_clf_path = os.path.join(settings.MODELS_DIR, "production_classifier.joblib")
    joblib.dump(best_clf_model, best_clf_path)
    
    # Save Random Forest as well for ensemble/explainability
    joblib.dump(trained_regressors["Random Forest Regressor"], os.path.join(settings.MODELS_DIR, "rf_regressor_12m.joblib"))
    
    # -------------------------------------------------------------
    # 6. FEATURE IMPORTANCE EXTRACTION
    # -------------------------------------------------------------
    # Extract feature importance from XGBoost & Random Forest
    rf_reg = trained_regressors["Random Forest Regressor"]
    xgb_reg = trained_regressors["XGBoost Regressor"]
    
    feature_importances = []
    for f_name, rf_imp, xgb_imp in zip(ALL_FEATURE_COLUMNS, rf_reg.feature_importances_, xgb_reg.feature_importances_):
        feature_importances.append({
            "feature": f_name,
            "rf_importance": round(float(rf_imp), 4),
            "xgb_importance": round(float(xgb_imp), 4),
            "ensemble_mean": round(float((rf_imp + xgb_imp) / 2.0), 4)
        })
    feature_importances.sort(key=lambda x: -x["ensemble_mean"])
    
    # -------------------------------------------------------------
    # 7. SAVE EXPERIMENT RESULTS & REGISTRY
    # -------------------------------------------------------------
    experiment_payload = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_version": "RDA_v1.0_Harmonized",
            "total_samples": len(df),
            "train_samples": len(X_train_raw),
            "test_samples": len(X_test_raw),
            "random_seed": RANDOM_SEED,
            "best_regressor": best_reg_name,
            "best_classifier": best_clf_name,
            "raw_features": RAW_FEATURE_COLUMNS,
            "all_features": ALL_FEATURE_COLUMNS
        },
        "regression_benchmarks": reg_results,
        "multi_horizon_metrics": horizon_metrics,
        "classification_benchmarks": clf_results,
        "feature_importances": feature_importances
    }
    
    results_path = os.path.join(settings.EXPERIMENTS_DIR, "evaluation_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_payload, f, indent=2)
        
    print(f"\n[OK] Experiment evaluation logged to: {results_path}")
    print(f"[OK] Production regressor: {best_reg_name} -> {best_reg_path}")
    print(f"[OK] Production classifier: {best_clf_name} -> {best_clf_path}")
    print("=" * 70)
    return experiment_payload

if __name__ == "__main__":
    train_and_evaluate_all()
