# RoadVision AI - Road Damage Detection and Severity Analysis

## Overview
RoadVision AI is a research prototype for AI-based road crack detection, experimental damage measurements, and Low/High severity classification.

## Features
- Road image upload
- AI crack detection and segmentation
- Approximate crack length, width, area, and coverage
- Experimental Low/High severity classification
- React-based analysis dashboard
- Downloadable analysis report
- One-click Windows demo launcher

## Technology Stack
- Frontend: React, Vite
- Backend: Python, FastAPI
- AI: YOLO-based crack segmentation and severity classification
- Model inference: Python

## Project Structure
- Models/ - AI model files
- road-damage-frontend/ - React dashboard
- api_server.py - FastAPI backend
- road_damage_app_v2.py - AI analysis functions
- requirements_road_damage_v2.txt - Python dependencies
- start_roadvision_demo.bat - Windows launcher

## Setup
Requirements: Windows, Python 3.12, Node.js and npm.

From this component directory:

1. Create a Python 3.12 virtual environment:
   py -3.12 -m venv .venv312

2. Install Python dependencies:
   .\.venv312\Scripts\python.exe -m pip install -r requirements_road_damage_v2.txt

3. Install the API dependencies if not already installed:
   .\.venv312\Scripts\python.exe -m pip install fastapi uvicorn python-multipart

4. Install frontend dependencies:
   cd road-damage-frontend
   npm install
   cd ..

5. Run start_roadvision_demo.bat

Frontend: http://localhost:5173
Backend: http://127.0.0.1:8000

## Research Limitations
- Metric measurements use an assumed image scale and are not calibrated physical measurements.
- Damage depth cannot be reliably measured from a single image.
- Low/High severity predictions are experimental and not expert-verified on RDA images.
- A validated 0-100 damage severity score has not been implemented.
- Detection performance is not guaranteed for every road image.

## Notes
Original RDA images, virtual environments, node_modules and backup archives are intentionally excluded from this repository.
