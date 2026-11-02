# Road Repair Priority System

This project focuses on road maintenance planning and repair prioritization using machine learning and historical road-condition data. It combines data preparation, feature engineering, model comparison, and prediction workflows for:

- road section priority classification
- repair cost estimation
- pavement repair method prediction
- maintenance planning using road and survey-related features

## Project purpose

The system analyzes road survey and repair data to help prioritize maintenance work based on factors such as road section characteristics, traffic load, nearby infrastructure, budget conditions, and historical repair patterns.

## Trained machine learning models

The repository currently contains the following trained model files in the `models/` directory:

| Model file | Description |
| --- | --- |
| `experimental_priority_classifier.joblib` | Experimental priority classification model for assigning road sections as Low, Medium, or High priority using a Decision Tree classifier. |
| `experimental_pavement_repair_model.joblib` | Experimental pavement repair method model for predicting repair actions such as pothole patching, crack sealing, and section overlay based on road section measurements. |
| `final_extra_trees_cost_model.joblib` | Final repair cost prediction model built with an Extra Trees Regressor to estimate repair cost from historical cost-related features. |
| `repair_cost_model.joblib` | Trained repair cost model for predicting repair cost using road repair data and relevant cost features. |
| `repair_cost_model_without_road_id.joblib` | Alternative repair cost model trained without the `RoadID` feature to evaluate cost prediction performance without road identity information. |

These models were trained and saved as joblib artifacts for reuse in prediction pipelines and further evaluation.

## Main project areas

- `datasets/` – road and maintenance datasets used for training and analysis
- `outputs/` – generated datasets, reports, feature outputs, and validation results
- `models/` – trained machine learning model files
- `backend/` – backend scripts for model inspection and project logic
- `frontend/` – React + Vite frontend for user-facing interaction
- `scripts and analysis files` – Python scripts for data cleaning, feature construction, model comparison, and validation

## Typical workflow

1. Prepare and clean road and maintenance data
2. Build feature sets for priority and cost prediction
3. Train and compare multiple machine learning algorithms
4. Save the best-performing models into `models/`
5. Use the trained models for priority estimation, cost prediction, and repair classification

## Example model usage

The saved models are standard `joblib` objects, so they can be loaded in Python as follows:

```python
import joblib

model = joblib.load("models/final_extra_trees_cost_model.joblib")
```

## Notes

- This project is designed for road maintenance analytics and predictive road repair planning.
- Model artifacts are stored in the repository for reuse and evaluation.
- Training and validation reports are kept in the project output folders for review.

## Repository status

This repository contains trained machine learning models and analysis outputs for road repair prioritization and cost estimation. The project is focused on data-driven maintenance decision support.
