
# STEP 649 - FastAPI Backend for RoadVision AI React Dashboard

import base64
import io
import math

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from starlette.concurrency import run_in_threadpool

from road_damage_app_v2 import (
    detect_cracks,
    measure_crack_pixels,
    classify_crack_regions,
    SEVERITY_THRESHOLD
)


# Create FastAPI application
app = FastAPI(
    title="RoadVision AI API",
    description="AI-Based Road Damage Analysis Research Prototype",
    version="2.0"
)

# Allow local React frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)


# Convert PIL images into browser-compatible data URLs
def image_to_data_url(image):

    buffer = io.BytesIO()

    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=85
    )

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"


# API health check
@app.get("/")
def home():

    return {
        "system": "RoadVision AI",
        "status": "API running",
        "version": "2.0"
    }


# Analyze uploaded road images
@app.post("/api/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    remove_rda_strip: bool = Form(False),
    assumed_mm_per_pixel: float = Form(2.0)
):

    # Validate the requested demonstration scale
    if (
        not math.isfinite(assumed_mm_per_pixel)
        or assumed_mm_per_pixel < 0
        or assumed_mm_per_pixel > 1000
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid demo scale."
        )

    # Read uploaded image
    file_bytes = await image.read()

    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image must be smaller than 15 MB."
        )

    try:
        uploaded_image = Image.open(
            io.BytesIO(file_bytes)
        ).convert("RGB")

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image."
        )

    # AI inference is CPU-intensive.
    # Run it outside the asynchronous request event loop.
    def process_image():

        # MODEL 1 - Crack Segmentation
        road_image, crack_result, crack_preview = detect_cracks(
            uploaded_image,
            remove_rda_strip=remove_rda_strip
        )

        # Experimental pixel measurements
        pixel_measurements = measure_crack_pixels(
            crack_result
        )

        # MODEL 2 - V2 Low/High Classification
        severity_preview, severity_predictions = (
            classify_crack_regions(
                road_image,
                crack_result
            )
        )

        detected_regions = (
            len(crack_result.boxes)
            if crack_result.boxes is not None
            else 0
        )

        # Default: physical measurements unavailable
        measurements = {
            "length_m": None,
            "width_m": None,
            "area_m2": None,
            "depth_m": None,
            "calibrated": False,
            "scale_verified": False
        }

        report = [
            "ROADVISION AI - ROAD DAMAGE ANALYSIS",
            "====================================",
            f"Detected Crack Regions: {detected_regions}",
            "",
            "EXPERIMENTAL CRACK MEASUREMENTS",
            "--------------------------------"
        ]

        if pixel_measurements is not None:

            length_px = pixel_measurements[
                "crack_length_px_approx"
            ]

            width_px = pixel_measurements[
                "average_width_px_approx"
            ]

            area_px2 = pixel_measurements[
                "crack_area_px2"
            ]

            coverage = pixel_measurements[
                "crack_coverage_percent"
            ]

            report.extend([
                f"Approx. Length: {length_px} pixels",
                f"Approx. Width: {width_px} pixels",
                f"Area: {area_px2} pixels squared",
                f"Crack Coverage: {coverage}%",
                ""
            ])

            # DEMO ONLY - Unverified physical scale
            if assumed_mm_per_pixel > 0:

                scale_m = assumed_mm_per_pixel / 1000

                measurements["length_m"] = round(
                    length_px * scale_m, 4
                )

                measurements["width_m"] = (
                    round(width_px * scale_m, 4)
                    if width_px is not None
                    else None
                )

                measurements["area_m2"] = round(
                    area_px2 * scale_m**2, 6
                )

                report.extend([
                    "DEMO METRIC ESTIMATES - NOT CALIBRATED",
                    f"Assumed Scale: {assumed_mm_per_pixel} mm/pixel",
                    f"Crack Length: {measurements['length_m']} m",
                    f"Average Width: {measurements['width_m']} m",
                    f"Crack Area: {measurements['area_m2']} m2",
                    ""
                ])

        else:

            report.extend([
                "No measurable crack mask detected.",
                "Length / Width / Area: NOT AVAILABLE",
                ""
            ])

        report.extend([
            "Crack Depth: N/A",
            "",
            "AI SEVERITY CLASSIFICATION",
            "--------------------------"
        ])

        if severity_predictions:

            for region in severity_predictions:

                report.extend([
                    f"Region: {region['region_id']}",
                    f"Predicted Severity: {region['predicted_severity']}",
                    f"Low Probability: {region['low_probability'] * 100:.2f}%",
                    f"High Probability: {region['high_probability'] * 100:.2f}%",
                    f"Near Threshold: {region['close_to_threshold']}",
                    "Expert Verified: NO",
                    ""
                ])

        else:

            report.append(
                "Severity: NOT ASSESSED"
            )

        report.extend([
            "",
            "RESEARCH LIMITATIONS",
            "--------------------",
            "1. Measurements are not calibrated.",
            "2. Metric values use an unverified demo scale.",
            "3. Severity predictions are experimental.",
            "4. Predictions are not expert verified.",
            "5. Class probability is not a 0-100 severity score.",
            "6. Crack depth is unavailable.",
            "7. Undetected road damage may still exist."
        ])

        return {
            "success": True,

            "detected_regions": detected_regions,

            "crack_image": image_to_data_url(
                crack_preview
            ),

            "severity_image": image_to_data_url(
                severity_preview
            ),

            "measurements": measurements,

            "severity_predictions": severity_predictions,

            "threshold": SEVERITY_THRESHOLD,

            "report": "\n".join(report),

            "research_prototype": True,

            "expert_verified": False
        }

    try:
        return await run_in_threadpool(process_image)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI analysis failed. Check the API terminal logs."
        )
