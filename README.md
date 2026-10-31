# RoadVision AI

### AI-Based Road Crack Detection and Severity Analysis

**Research prototype | Road Damage Detection & Severity Analysis component**

RoadVision AI is a web-based research prototype that analyzes uploaded road images using computer vision. It highlights detected cracks, estimates their visible dimensions, predicts **LOW** or **HIGH** severity for detected crack regions, and generates a downloadable analysis report.

> **Research status:** This is an experimental prototype, not a certified road inspection or maintenance decision system. Physical measurements are not calibrated, and severity predictions require further expert validation.

## Key Features

- **Road image upload:** Supports JPG, PNG, and WebP images in the dashboard.
- **AI crack segmentation:** Highlights predicted crack regions on road images.
- **Experimental measurements:** Estimates crack length, average width, area, and surface coverage from segmentation masks.
- **Severity classification:** Predicts LOW or HIGH severity for each detected crack region.
- **Visual dashboard:** Displays the original image, crack segmentation, severity visualization, and results.
- **Downloadable report:** Exports a text-based analysis report.
- **Optional RDA image preprocessing:** Can remove the bottom metadata strip from compatible road images.
- **Windows demo launcher:** Starts the backend and frontend using a batch file after dependencies are installed.

## How It Works

```text
Road image upload
       |
       v
Crack detection and segmentation (Model 1)
       |
       +--> Experimental crack pixel measurements
       |
       v
Detected crack region crops
       |
       v
LOW / HIGH severity classification (Model 2)
       |
       v
Dashboard visualizations and downloadable report
```

### AI Models

| Model | File | Purpose |
| --- | --- | --- |
| Pretrained crack segmentation model | `Models/crack_detection_model.onnx` | Detects and segments road cracks |
| YOLO11 Nano Balanced V2 classifier | `Models/attain_severity_classifier_balanced_v2_best.pt` | Predicts LOW or HIGH severity |

The **crack segmentation model is pretrained** and integrated into this application. The **severity classification model was trained and evaluated separately** using Attain road-damage image crops.

The classifier uses a validation-selected **HIGH decision threshold of `0.4413`**. Classification probabilities are **not** a numerical road-severity score.

## Technologies

| Layer | Technologies |
| --- | --- |
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI, Uvicorn |
| Computer vision | Ultralytics YOLO, OpenCV, Pillow, NumPy, scikit-image |
| AI model formats | ONNX and PyTorch `.pt` |

## Repository Structure

This component is located inside the group repository at `road-damage-detection-severity-analysis/`.

```text
road-damage-detection-severity-analysis/
├── Models/
│   ├── crack_detection_model.onnx
│   └── attain_severity_classifier_balanced_v2_best.pt
├── road-damage-frontend/
│   ├── public/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── api_server.py
├── road_damage_app_v2.py
├── requirements_road_damage_v2.txt
├── start_roadvision_demo.bat
└── README.md
```

## Getting Started (Windows)

### Prerequisites

- Windows 10/11
- Python **3.12** (available through the `py` launcher)
- Node.js and npm
- Git (if cloning the repository)

### 1. Clone the group repository

```powershell
git clone --branch road-damage-detection-severity-analysis https://github.com/PethmiThotawaththa/J26-IT-336.git
cd J26-IT-336\road-damage-detection-severity-analysis
```

If you already cloned the repository, switch to the `road-damage-detection-severity-analysis` branch before entering the component directory.

### 2. Create a Python environment

Run the following from the **component folder**:

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install --upgrade pip
.\.venv312\Scripts\python.exe -m pip install -r requirements_road_damage_v2.txt
.\.venv312\Scripts\python.exe -m pip install fastapi uvicorn python-multipart
```

### 3. Install frontend dependencies

```powershell
cd road-damage-frontend
npm install
cd ..
```

### 4. Run the application

**Option A — Windows demo launcher**

Double-click `start_roadvision_demo.bat` from the component folder, or run:

```powershell
.\start_roadvision_demo.bat
```

Check both terminal windows for errors and confirm that the backend and frontend servers are running.

**Option B — Start the servers manually**

Terminal 1 (from the component directory):

```powershell
.\.venv312\Scripts\python.exe -m uvicorn api_server:app --host 127.0.0.1 --port 8000
```

Terminal 2 (from the component directory):

```powershell
cd road-damage-frontend
npm run dev
```

Open the dashboard at **http://localhost:5173**. The local API runs at **http://127.0.0.1:8000**.

## Using the Dashboard

1. Upload a clear road-surface image (JPG, PNG, or WebP).
2. Optionally choose **Remove RDA bottom metadata strip** for images that include this strip.
3. Review the **unverified demo scale** setting (mm/pixel); this is not a calibrated physical scale.
4. Click **Run AI Analysis**.
5. View the crack segmentation, estimated measurements, and LOW/HIGH severity predictions.
6. Click **Download Analysis Report** to save the text report.

The API accepts a `POST` request to `/api/analyze` with an image and optional analysis settings. The backend also has a health-check endpoint at `GET /`.

## Experimental Evaluation

The Balanced V2 severity classifier achieved the following **Attain holdout test results** in the project experiments:

| Metric | Result |
| --- | ---: |
| Test images | 1,165 |
| Test accuracy | 85.75% |
| Balanced accuracy | 72.18% |
| HIGH-class recall | 55.45% |

These figures refer **only to severity classification on the Attain test set**. They do not represent overall website accuracy, crack segmentation accuracy, or validated performance on Sri Lankan RDA images.

## Research Limitations

- **Uncalibrated sizes:** The length, width, and area are based on image segmentation and an assumed mm/pixel scale. They are **demonstration estimates**, not verified physical measurements.
- **No depth measurement:** Crack depth cannot be established reliably from a single ordinary road image in this prototype.
- **Experimental severity:** LOW/HIGH predictions are not yet verified by road engineering experts on the intended deployment data.
- **No validated 0–100 score:** Model probabilities are not a standardized severity index.
- **Limited generalization evidence:** Independent validation on more Sri Lankan road images, lighting conditions, and damage types is still needed.
- **Crack-focused implementation:** This prototype does not claim comprehensive detection and severity assessment of every road-damage type.

## Future Improvements

- Calibrate physical measurements using reliable real-world scale information.
- Improve HIGH-severity classification and test robustness on additional road images.
- Carry out independent evaluation using labeled Sri Lankan road datasets and domain-expert feedback.
- Investigate broader road-damage categories and integration with road-maintenance planning.

## Project Notes

- The repository intentionally excludes raw RDA datasets, local Python virtual environments, `node_modules`, and personal backup archives.
- The AI models are included for prototype inference. Before reuse or redistribution, review the original pretrained model's license and dataset usage conditions.
- This is an individual research component within the **J26-IT-336** group repository and is maintained on the `road-damage-detection-severity-analysis` feature branch until merged by the project team.

---

**RoadVision AI — Research Prototype V2**
