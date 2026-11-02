# Road Repair Priority System

A road-maintenance decision-support project that uses road survey and repair data to estimate repair costs, classify possible pavement repair methods, and assign provisional maintenance priorities to road sections.

The repository includes data preparation and analysis scripts, saved machine-learning models, a FastAPI backend, and a React frontend.

## Features

- Estimate road repair costs in Sri Lankan Rupees (LKR).
- Predict a pavement repair method: pothole patching, crack sealing, or section overlay.
- Classify a road section's provisional maintenance/inspection priority as Low, Medium, or High.
- Inspect saved model availability through the backend API.
- Prepare and analyze road, traffic, weather, budget, and repair data using Python scripts.

## Trained models

The saved model artifacts are in `models/`.

| Model artifact | Algorithm / purpose | Used by backend |
| --- | --- | :---: |
| `final_extra_trees_cost_model.joblib` | Extra Trees regressor for repair-cost estimates. | Yes |
| `experimental_pavement_repair_model.joblib` | Extra Trees classifier for repair-method predictions. | Yes |
| `experimental_priority_classifier.joblib` | Decision Tree classifier for experimental Low/Medium/High priority predictions. | Yes |
| `repair_cost_model.joblib` | Previously trained repair-cost model retained for comparison and analysis. | No |
| `repair_cost_model_without_road_id.joblib` | Alternative repair-cost model trained without road ID information. | No |

The priority classifier was trained with a small set of manually labelled sections and is experimental. Treat its output as provisional decision support, not as a definitive engineering assessment. Cost estimates are based on historical patterns and should be reviewed before budgeting or procurement decisions.

## Repository structure

```text
Road_Repair_Priority_System/
├── backend/
│   ├── main.py                 # FastAPI API and prediction endpoints
│   └── inspect_models.py       # Read-only model inspection utility
├── datasets/
│   └── road_surveys/           # Road survey input data
├── frontend/
│   ├── src/                    # React application source
│   ├── package.json            # Frontend dependencies and scripts
│   └── README.md               # Frontend template notes
├── models/                     # Saved joblib model artifacts
├── outputs/                    # Prepared datasets and generated results
├── *.py                        # Training, prediction, preparation, and analysis scripts
├── *_report.txt                # Model, data, and validation reports
└── README.md                   # Project documentation
```

The repository also contains a root-level `main.py` for combining road survey CSV files into `outputs/combined_road_surveys.csv`.

## Technologies

### Backend and machine learning

- Python 3 (the current project virtual environment uses Python 3.13.7)
- FastAPI and Uvicorn (REST API and ASGI server)
- scikit-learn (machine-learning estimators and pipelines)
- pandas and NumPy (data preparation and feature handling)
- joblib (loading and saving trained models)
- Pydantic (API request validation)

### Frontend

- React 19
- Vite
- Tailwind CSS
- lucide-react
- Oxlint

## Python environment setup

Run these commands from the project root (`Road_Repair_Priority_System`). Python 3.13.7 is the version available in the existing project environment; using the same Python and compatible scikit-learn versions is recommended when loading the saved models.

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn joblib pandas scikit-learn
```

If PowerShell prevents environment activation, either allow activation according to your local policy or call the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn joblib pandas scikit-learn
```

There is currently no Python `requirements.txt` or `pyproject.toml` in the project, so the packages above are installed explicitly. Individual data-analysis scripts may use additional packages; install those only if a script reports a missing dependency.

## Run the backend

From the project root, activate the virtual environment and start the API:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --port 8000
```

The API will be available at:

- API root: <http://127.0.0.1:8000/>
- Health check: <http://127.0.0.1:8000/api/health>
- Loaded model status: <http://127.0.0.1:8000/api/models/status>
- Interactive API documentation: <http://127.0.0.1:8000/docs>

The backend loads the three models it serves from `models/` when it starts. Check the model-status endpoint if a model file is missing or could not be loaded.

## Run the frontend

Open a second terminal and run:

```powershell
cd frontend
npm install
npm run dev
```

Open the dashboard at <http://localhost:5174/> after the development server starts. The frontend calls the backend at `http://127.0.0.1:8000`, so start the backend as well to use prediction features.

Other frontend commands, run from `frontend/`:

```powershell
npm run build
npm run preview
npm run lint
```

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Backend status |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/models/status` | Loaded model status |
| `POST` | `/api/predict/cost` | Predict repair cost |
| `POST` | `/api/predict/method` | Predict pavement repair method |
| `POST` | `/api/predict/priority` | Predict provisional repair priority |

Use the interactive documentation at `/docs` to see each endpoint's request fields and try requests.

## Data and model workflow

1. Prepare or clean the relevant road survey and maintenance data.
2. Generate the required feature datasets with the relevant scripts.
3. Train or evaluate models using the training and comparison scripts.
4. Save model artifacts in `models/`.
5. Start the API and use its prediction endpoints or the frontend.

Training, analysis, and validation reports (`*_report.txt`) are kept in the project root and `outputs/` where applicable. Review the corresponding reports and source scripts for dataset assumptions and evaluation details. Training a model on all available records is not, by itself, an estimate of its performance on unseen roads.

## Notes

- Run project scripts from the project root unless a script's own instructions specify otherwise; some scripts use paths relative to the current working directory.
- Keep the required model artifacts in `models/` for the backend's prediction endpoints.
- Predictions are decision-support estimates and should be validated against current road conditions and engineering expertise.
