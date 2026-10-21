
# ============================================================
# AI-BASED ROAD DAMAGE ANALYSIS APPLICATION - VERSION 2
# ============================================================
#
# Features:
# 1. AI Crack Detection and Segmentation
# 2. Experimental Crack Measurements
# 3. YOLO11 V2 Low/High Severity Classification
#
# IMPORTANT:
# - Severity predictions are experimental.
# - Measurements are in pixels unless separately converted.
# - Probabilities are NOT numerical severity scores (0-100).
# ============================================================


# ------------------------------------------------------------
# STEP 600 - Application Configuration
# ------------------------------------------------------------

from pathlib import Path

import numpy as np
import cv2

from PIL import Image, ImageDraw
from ultralytics import YOLO
from skimage.morphology import skeletonize


# Main project directory
BASE_DIR = Path(__file__).resolve().parent

# Folder containing trained AI models
MODELS_DIR = BASE_DIR / "Models"

# MODEL 1 - Crack Detection and Segmentation
CRACK_MODEL_PATH = (
    MODELS_DIR / "crack_detection_model.onnx"
)

# MODEL 2 - Trained Low/High Severity Classifier V2
SEVERITY_V2_MODEL_PATH = (
    MODELS_DIR
    / "attain_severity_classifier_balanced_v2_best.pt"
)

# Threshold selected using Attain validation data
SEVERITY_THRESHOLD = 0.4413


print("ROAD DAMAGE AI APPLICATION")
print("--------------------------")
print("Crack Model Found:", CRACK_MODEL_PATH.exists())
print("Severity V2 Model Found:", SEVERITY_V2_MODEL_PATH.exists())


# ------------------------------------------------------------
# STEP 602 - Load AI Models
# ------------------------------------------------------------

print("\nLOADING AI MODELS...")
print("--------------------------")

# Model 1 - Crack Segmentation
crack_model = YOLO(
    str(CRACK_MODEL_PATH),
    task="segment"
)

print("Crack Segmentation Model: LOADED")


# Model 2 - Low/High Severity Classification
severity_v2_model = YOLO(
    str(SEVERITY_V2_MODEL_PATH),
    task="classify"
)

print("Severity Classifier V2: LOADED")

print("\nAI MODEL LOADING COMPLETED!")


# ------------------------------------------------------------
# STEP 610 - Detect Cracks
# ------------------------------------------------------------

def detect_cracks(image, remove_rda_strip=False):

    if image is None:
        return None, None, None

    # Convert uploaded image into RGB format
    road_image = image.convert("RGB")

    # Remove metadata strip only when required
    if remove_rda_strip:
        road_image = road_image.crop(
            (
                0,
                0,
                road_image.width,
                int(road_image.height * 0.88)
            )
        )

    # Predict crack segmentation regions
    crack_result = crack_model.predict(
        source=road_image,
        conf=0.25,
        imgsz=640,
        device="cpu",
        verbose=False
    )[0]

    # Visualize predicted cracks
    annotated_image = Image.fromarray(
        crack_result.plot()[..., ::-1]
    )

    return road_image, crack_result, annotated_image


# ------------------------------------------------------------
# STEP 614 - Experimental Crack Pixel Measurements
# ------------------------------------------------------------

def measure_crack_pixels(crack_result):

    # No predicted segmentation mask
    if (
        crack_result is None
        or crack_result.masks is None
    ):
        return None

    height, width = crack_result.orig_shape

    # Empty binary mask
    mask = np.zeros(
        (height, width),
        dtype=np.uint8
    )

    # Combine detected crack polygons
    for polygon in crack_result.masks.xy:

        if len(polygon) >= 3:

            points = np.round(
                polygon
            ).astype(np.int32)

            cv2.fillPoly(
                mask,
                [points],
                1
            )

    # Crack area in square pixels
    area_px2 = int(
        np.count_nonzero(mask)
    )

    if area_px2 == 0:
        return None

    # Skeletonize detected crack mask
    skeleton = skeletonize(
        mask.astype(bool)
    )

    # Approximate skeleton pixel distances
    horizontal = np.count_nonzero(
        skeleton[:, :-1] & skeleton[:, 1:]
    )

    vertical = np.count_nonzero(
        skeleton[:-1, :] & skeleton[1:, :]
    )

    diagonal_1 = np.count_nonzero(
        skeleton[:-1, :-1] & skeleton[1:, 1:]
    )

    diagonal_2 = np.count_nonzero(
        skeleton[:-1, 1:] & skeleton[1:, :-1]
    )

    # Experimental crack length
    length_px = (
        horizontal
        + vertical
        + np.sqrt(2) * (diagonal_1 + diagonal_2)
    )

    # Experimental average width
    width_px = (
        area_px2 / length_px
        if length_px > 0
        else None
    )

    # Crack coverage percentage
    coverage_percent = (
        area_px2 / (height * width)
    ) * 100

    return {
        "crack_area_px2": area_px2,

        "crack_length_px_approx": round(
            float(length_px), 2
        ),

        "average_width_px_approx": (
            round(float(width_px), 2)
            if width_px is not None
            else None
        ),

        "crack_coverage_percent": round(
            coverage_percent, 4
        )
    }


# ------------------------------------------------------------
# STEP 617 - V2 Severity Classification
# ------------------------------------------------------------

def classify_crack_regions(
    road_image,
    crack_result
):

    """
    Classify each AI-detected crack region as LOW or HIGH.

    Returns:
        severity_preview:
            Image showing severity labels and boxes.

        severity_reports:
            List containing severity predictions for
            detected crack regions.

    Important:
        Predictions are experimental and not expert-verified.
    """

    # Validate input
    if road_image is None or crack_result is None:
        return None, []

    # Create a copy for drawing results
    severity_preview = road_image.copy().convert("RGB")

    draw = ImageDraw.Draw(
        severity_preview
    )

    severity_reports = []

    # Check for detected crack regions
    if (
        crack_result.boxes is None
        or crack_result.masks is None
        or len(crack_result.boxes) == 0
    ):

        print(
            "No detected crack regions available "
            "for severity classification."
        )

        return severity_preview, severity_reports

    # Crack bounding boxes
    crack_boxes = (
        crack_result.boxes.xyxy
        .cpu()
        .numpy()
    )

    # Read V2 classifier class names
    class_names = severity_v2_model.names

    # Identify LOW and HIGH class indices
    low_id = next(
        class_id
        for class_id, name in class_names.items()
        if name.lower() == "low"
    )

    high_id = next(
        class_id
        for class_id, name in class_names.items()
        if name.lower() == "high"
    )

    # Classify each detected crack region
    for index, box in enumerate(
        crack_boxes,
        start=1
    ):

        x1, y1, x2, y2 = box

        # Add 10% surrounding context
        pad_x = max(
            10,
            (x2 - x1) * 0.10
        )

        pad_y = max(
            10,
            (y2 - y1) * 0.10
        )

        # Keep coordinates inside image
        left = max(
            0,
            int(x1 - pad_x)
        )

        top = max(
            0,
            int(y1 - pad_y)
        )

        right = min(
            road_image.width,
            int(np.ceil(x2 + pad_x))
        )

        bottom = min(
            road_image.height,
            int(np.ceil(y2 + pad_y))
        )

        # Skip invalid boxes
        if right <= left or bottom <= top:
            continue

        # Crop detected crack region
        crack_crop = road_image.crop(
            (
                left,
                top,
                right,
                bottom
            )
        )

        # ----------------------------------------------------
        # Predict LOW/HIGH using trained V2 classification model
        # ----------------------------------------------------

        prediction = severity_v2_model.predict(
            source=crack_crop,
            imgsz=224,
            device="cpu",
            verbose=False
        )[0]

        if prediction.probs is None:
            print(
                f"Region {index}: "
                "No classification probabilities available."
            )
            continue

        # Obtain class probabilities
        probabilities = (
            prediction.probs.data
            .cpu()
            .numpy()
        )

        low_prob = float(
            probabilities[low_id]
        )

        high_prob = float(
            probabilities[high_id]
        )

        # Apply validation-selected threshold
        if high_prob >= SEVERITY_THRESHOLD:

            severity_label = "HIGH"
            color = "red"

        else:

            severity_label = "LOW"
            color = "yellow"

        # Check if prediction is near threshold
        close_to_threshold = (
            abs(high_prob - SEVERITY_THRESHOLD) < 0.05
        )

        # Draw region bounding box
        draw.rectangle(
            [left, top, right, bottom],
            outline=color,
            width=3
        )

        # Draw severity label
        label_text = (
            f"{severity_label} "
            f"(High p={high_prob * 100:.1f}%)"
        )

        text_y = (
            top - 18
            if top > 20
            else top + 5
        )

        draw.text(
            (left, text_y),
            label_text,
            fill=color
        )

        # Store prediction details
        severity_reports.append({

            "region_id": index,

            "crop_box": [
                left,
                top,
                right,
                bottom
            ],

            "predicted_severity": severity_label,

            "low_probability": round(
                low_prob, 4
            ),

            "high_probability": round(
                high_prob, 4
            ),

            "threshold": SEVERITY_THRESHOLD,

            "close_to_threshold": close_to_threshold,

            "expert_verified": False,

            "severity_score_0_100": None
        })

    return severity_preview, severity_reports

# ============================================================
# AI-BASED ROAD DAMAGE ANALYSIS APPLICATION - VERSION 2
# ============================================================
#
# Features:
# 1. AI Crack Detection and Segmentation
# 2. Experimental Crack Measurements
# 3. YOLO11 V2 Low/High Severity Classification
#
# IMPORTANT:
# - Severity predictions are experimental.
# - Measurements are in pixels unless separately converted.
# - Probabilities are NOT numerical severity scores (0-100).
# ============================================================


# ------------------------------------------------------------
# STEP 600 - Application Configuration
# ------------------------------------------------------------

from pathlib import Path

import numpy as np
import cv2

from PIL import Image, ImageDraw
from ultralytics import YOLO
from skimage.morphology import skeletonize


# Main project directory
BASE_DIR = Path(__file__).resolve().parent

# Folder containing trained AI models
MODELS_DIR = BASE_DIR / "Models"

# MODEL 1 - Crack Detection and Segmentation
CRACK_MODEL_PATH = (
    MODELS_DIR / "crack_detection_model.onnx"
)

# MODEL 2 - Trained Low/High Severity Classifier V2
SEVERITY_V2_MODEL_PATH = (
    MODELS_DIR
    / "attain_severity_classifier_balanced_v2_best.pt"
)

# Threshold selected using Attain validation data
SEVERITY_THRESHOLD = 0.4413


print("ROAD DAMAGE AI APPLICATION")
print("--------------------------")
print("Crack Model Found:", CRACK_MODEL_PATH.exists())
print("Severity V2 Model Found:", SEVERITY_V2_MODEL_PATH.exists())


# ------------------------------------------------------------
# STEP 602 - Load AI Models
# ------------------------------------------------------------

print("\nLOADING AI MODELS...")
print("--------------------------")

# Model 1 - Crack Segmentation
crack_model = YOLO(
    str(CRACK_MODEL_PATH),
    task="segment"
)

print("Crack Segmentation Model: LOADED")


# Model 2 - Low/High Severity Classification
severity_v2_model = YOLO(
    str(SEVERITY_V2_MODEL_PATH),
    task="classify"
)

print("Severity Classifier V2: LOADED")

print("\nAI MODEL LOADING COMPLETED!")


# ------------------------------------------------------------
# STEP 610 - Detect Cracks
# ------------------------------------------------------------

def detect_cracks(image, remove_rda_strip=False):

    if image is None:
        return None, None, None

    # Convert uploaded image into RGB format
    road_image = image.convert("RGB")

    # Remove metadata strip only when required
    if remove_rda_strip:
        road_image = road_image.crop(
            (
                0,
                0,
                road_image.width,
                int(road_image.height * 0.88)
            )
        )

    # Predict crack segmentation regions
    crack_result = crack_model.predict(
        source=road_image,
        conf=0.25,
        imgsz=640,
        device="cpu",
        verbose=False
    )[0]

    # Visualize predicted cracks
    annotated_image = Image.fromarray(
        crack_result.plot()[..., ::-1]
    )

    return road_image, crack_result, annotated_image


# ------------------------------------------------------------
# STEP 614 - Experimental Crack Pixel Measurements
# ------------------------------------------------------------

def measure_crack_pixels(crack_result):

    # No predicted segmentation mask
    if (
        crack_result is None
        or crack_result.masks is None
    ):
        return None

    height, width = crack_result.orig_shape

    # Empty binary mask
    mask = np.zeros(
        (height, width),
        dtype=np.uint8
    )

    # Combine detected crack polygons
    for polygon in crack_result.masks.xy:

        if len(polygon) >= 3:

            points = np.round(
                polygon
            ).astype(np.int32)

            cv2.fillPoly(
                mask,
                [points],
                1
            )

    # Crack area in square pixels
    area_px2 = int(
        np.count_nonzero(mask)
    )

    if area_px2 == 0:
        return None

    # Skeletonize detected crack mask
    skeleton = skeletonize(
        mask.astype(bool)
    )

    # Approximate skeleton pixel distances
    horizontal = np.count_nonzero(
        skeleton[:, :-1] & skeleton[:, 1:]
    )

    vertical = np.count_nonzero(
        skeleton[:-1, :] & skeleton[1:, :]
    )

    diagonal_1 = np.count_nonzero(
        skeleton[:-1, :-1] & skeleton[1:, 1:]
    )

    diagonal_2 = np.count_nonzero(
        skeleton[:-1, 1:] & skeleton[1:, :-1]
    )

    # Experimental crack length
    length_px = (
        horizontal
        + vertical
        + np.sqrt(2) * (diagonal_1 + diagonal_2)
    )

    # Experimental average width
    width_px = (
        area_px2 / length_px
        if length_px > 0
        else None
    )

    # Crack coverage percentage
    coverage_percent = (
        area_px2 / (height * width)
    ) * 100

    return {
        "crack_area_px2": area_px2,

        "crack_length_px_approx": round(
            float(length_px), 2
        ),

        "average_width_px_approx": (
            round(float(width_px), 2)
            if width_px is not None
            else None
        ),

        "crack_coverage_percent": round(
            coverage_percent, 4
        )
    }


# ------------------------------------------------------------
# STEP 617 - V2 Severity Classification
# ------------------------------------------------------------

def classify_crack_regions(
    road_image,
    crack_result
):

    """
    Classify each AI-detected crack region as LOW or HIGH.

    Returns:
        severity_preview:
            Image showing severity labels and boxes.

        severity_reports:
            List containing severity predictions for
            detected crack regions.

    Important:
        Predictions are experimental and not expert-verified.
    """

    # Validate input
    if road_image is None or crack_result is None:
        return None, []

    # Create a copy for drawing results
    severity_preview = road_image.copy().convert("RGB")

    draw = ImageDraw.Draw(
        severity_preview
    )

    severity_reports = []

    # Check for detected crack regions
    if (
        crack_result.boxes is None
        or crack_result.masks is None
        or len(crack_result.boxes) == 0
    ):

        print(
            "No detected crack regions available "
            "for severity classification."
        )

        return severity_preview, severity_reports

    # Crack bounding boxes
    crack_boxes = (
        crack_result.boxes.xyxy
        .cpu()
        .numpy()
    )

    # Read V2 classifier class names
    class_names = severity_v2_model.names

    # Identify LOW and HIGH class indices
    low_id = next(
        class_id
        for class_id, name in class_names.items()
        if name.lower() == "low"
    )

    high_id = next(
        class_id
        for class_id, name in class_names.items()
        if name.lower() == "high"
    )

    # Classify each detected crack region
    for index, box in enumerate(
        crack_boxes,
        start=1
    ):

        x1, y1, x2, y2 = box

        # Add 10% surrounding context
        pad_x = max(
            10,
            (x2 - x1) * 0.10
        )

        pad_y = max(
            10,
            (y2 - y1) * 0.10
        )

        # Keep coordinates inside image
        left = max(
            0,
            int(x1 - pad_x)
        )

        top = max(
            0,
            int(y1 - pad_y)
        )

        right = min(
            road_image.width,
            int(np.ceil(x2 + pad_x))
        )

        bottom = min(
            road_image.height,
            int(np.ceil(y2 + pad_y))
        )

        # Skip invalid boxes
        if right <= left or bottom <= top:
            continue

        # Crop detected crack region
        crack_crop = road_image.crop(
            (
                left,
                top,
                right,
                bottom
            )
        )

        # ----------------------------------------------------
        # Predict LOW/HIGH using trained V2 classification model
        # ----------------------------------------------------

        prediction = severity_v2_model.predict(
            source=crack_crop,
            imgsz=224,
            device="cpu",
            verbose=False
        )[0]

        if prediction.probs is None:
            print(
                f"Region {index}: "
                "No classification probabilities available."
            )
            continue

        # Obtain class probabilities
        probabilities = (
            prediction.probs.data
            .cpu()
            .numpy()
        )

        low_prob = float(
            probabilities[low_id]
        )

        high_prob = float(
            probabilities[high_id]
        )

        # Apply validation-selected threshold
        if high_prob >= SEVERITY_THRESHOLD:

            severity_label = "HIGH"
            color = "red"

        else:

            severity_label = "LOW"
            color = "yellow"

        # Check if prediction is near threshold
        close_to_threshold = (
            abs(high_prob - SEVERITY_THRESHOLD) < 0.05
        )

        # Draw region bounding box
        draw.rectangle(
            [left, top, right, bottom],
            outline=color,
            width=3
        )

        # Draw severity label
        label_text = (
            f"{severity_label} "
            f"(High p={high_prob * 100:.1f}%)"
        )

        text_y = (
            top - 18
            if top > 20
            else top + 5
        )

        draw.text(
            (left, text_y),
            label_text,
            fill=color
        )

        # Store prediction details
        severity_reports.append({

            "region_id": index,

            "crop_box": [
                left,
                top,
                right,
                bottom
            ],

            "predicted_severity": severity_label,

            "low_probability": round(
                low_prob, 4
            ),

            "high_probability": round(
                high_prob, 4
            ),

            "threshold": SEVERITY_THRESHOLD,

            "close_to_threshold": close_to_threshold,

            "expert_verified": False,

            "severity_score_0_100": None
        })

    return severity_preview, severity_reports



# STEP 624 - Combined AI Road Damage Analysis

def analyze_road_image(
    image,
    remove_rda_strip,
    assumed_mm_per_pixel
):

    if image is None:
        return None, None, "Please upload a road image."

    # 1. Detect cracks
    road_image, crack_result, crack_preview = detect_cracks(
        image,
        remove_rda_strip=remove_rda_strip
    )

    # 2. Calculate experimental measurements
    measurements = measure_crack_pixels(crack_result)

    # 3. Predict LOW/HIGH severity for detected crack regions
    severity_preview, severity_reports = classify_crack_regions(
        road_image,
        crack_result
    )

    # 4. Prepare report
    report = [
        "AI ROAD DAMAGE ANALYSIS REPORT",
        "================================",
        "",
        f"Detected Crack Regions: {len(severity_reports)}",
        "",
        "CRACK MEASUREMENTS",
        "------------------"
    ]

    if measurements is not None:

        report.append(
            f"Crack Area: {measurements['crack_area_px2']} px²"
        )

        report.append(
            f"Approx. Crack Length: "
            f"{measurements['crack_length_px_approx']} px"
        )

        report.append(
            f"Approx. Average Width: "
            f"{measurements['average_width_px_approx']} px"
        )

        report.append(
            f"Crack Coverage: "
            f"{measurements['crack_coverage_percent']}%"
        )

        # Metric conversion is DEMO ONLY
        if (
            assumed_mm_per_pixel is not None
            and assumed_mm_per_pixel > 0
        ):

            scale = assumed_mm_per_pixel / 1000.0

            length_m = (
                measurements["crack_length_px_approx"] * scale
            )

            width_px = measurements[
                "average_width_px_approx"
            ]

            area_m2 = (
                measurements["crack_area_px2"] * scale**2
            )

            report.extend([
                "",
                "DEMO METRIC ESTIMATES - NOT CALIBRATED",
                f"Assumed Scale: {assumed_mm_per_pixel} mm/pixel",
                f"Crack Length: {length_m:.4f} m",
                (
                    f"Average Width: {width_px * scale:.4f} m"
                    if width_px is not None
                    else "Average Width: N/A"
                ),
                f"Crack Area: {area_m2:.6f} m²"
            ])

        report.append("Crack Depth: N/A")

    else:
        report.extend([
            "No measurable segmentation mask detected.",
            "Length, Width and Area: NOT AVAILABLE",
            "Crack Depth: N/A"
        ])

    # 5. Severity classification report
    report.extend([
        "",
        "AI SEVERITY CLASSIFICATION",
        "--------------------------"
    ])

    if severity_reports:

        for region in severity_reports:

            report.extend([
                f"Region: {region['region_id']}",
                f"Predicted Class: {region['predicted_severity']}",
                (
                    f"Low Probability: "
                    f"{region['low_probability'] * 100:.2f}%"
                ),
                (
                    f"High Probability: "
                    f"{region['high_probability'] * 100:.2f}%"
                ),
                (
                    f"Near Threshold: "
                    f"{region['close_to_threshold']}"
                ),
                "Expert Verified: NO",
                ""
            ])

    else:
        report.append(
            "Severity: NOT ASSESSED"
        )

    report.extend([
        "",
        "IMPORTANT LIMITATIONS",
        "--------------------------",
        "1. Predictions are experimental.",
        "2. Results are not expert verified.",
        "3. Metric estimates use an unverified scale.",
        "4. Class probability is NOT a 0-100 severity score.",
        "5. Crack depth cannot be determined from this image.",
        "6. Undetected damage may still be present."
    ])

    return (
        crack_preview,
        severity_preview,
        "\n".join(report)
    )



# STEP 625 - Final Gradio Web Application

import gradio as gr


def create_web_app():

    app = gr.Interface(
        fn=analyze_road_image,

        inputs=[
            gr.Image(
                type="pil",
                label="Upload Road Damage Image"
            ),

            gr.Checkbox(
                value=False,
                label="Remove bottom metadata strip (RDA images only)"
            ),

            gr.Number(
                value=2.0,
                label="UNVERIFIED DEMO Scale (mm/pixel)"
            )
        ],

        outputs=[
            gr.Image(
                type="pil",
                label="AI Crack Segmentation"
            ),

            gr.Image(
                type="pil",
                label="AI V2 Low/High Severity Classification"
            ),

            gr.Textbox(
                label="Road Damage Analysis Report",
                lines=22
            )
        ],

        title="AI-Based Road Damage Analysis System",

        description=(
            "Research Prototype | Crack Segmentation, "
            "Experimental Measurements and AI-Based "
            "Low/High Severity Classification. "
            "Physical scale is unverified. "
            "Results are not expert validated."
        )
    )

    return app


# Run only when this file is executed directly
if __name__ == "__main__":

    print("\nSTARTING ROAD DAMAGE WEB APPLICATION...")

    web_app = create_web_app()

    web_app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )
