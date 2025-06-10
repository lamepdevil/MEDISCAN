from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import os
import shutil
import pytesseract
from PIL import Image, UnidentifiedImageError
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Initialize app
app = FastAPI()

# Enable CORS for all domains (configurable)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories and data stores
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define keywords for each report type
report_keywords = {
    "blood": ["hemoglobin", "rbc", "wbc"],
    "glucose": ["glucose", "sugar"],
    "cholesterol": ["hdl", "ldl", "cholesterol"]
}

# Initialize report history
report_history: Dict[str, list] = {rtype: [] for rtype in report_keywords}

# --- Utility Functions ---

def extract_text_from_image(image_path: str) -> str:
    """Extract text using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        return pytesseract.image_to_string(img).lower()
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Unsupported image format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

def determine_report_type(text: str) -> str:
    """Determine report type from keywords."""
    for rtype, keywords in report_keywords.items():
        if any(keyword in text for keyword in keywords):
            return rtype
    return "unknown"

def save_chart(data_list, label: str) -> str:
    """Create chart from data and return as base64 string."""
    plt.figure(figsize=(6, 4))
    plt.plot(data_list, marker='o', linestyle='-', color='blue')
    plt.title(f"{label} Levels Over Time")
    plt.xlabel("Test #")
    plt.ylabel(label)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_b64}"

# --- API Route ---

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    """Upload an image and return analysis results."""
    filename = file.filename
    if not (filename.lower().endswith((".png", ".jpg", ".jpeg"))):
        raise HTTPException(status_code=400, detail="Only PNG and JPG images are supported.")

    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text and classify report
    extracted_text = extract_text_from_image(file_path)
    report_type = determine_report_type(extracted_text)

    # Simulate data extraction (replace with real logic)
    charts = {}
    if report_type in report_history:
        simulated_value = 100 + len(report_history[report_type]) * 5
        report_history[report_type].append(simulated_value)
        charts[report_type] = save_chart(report_history[report_type], report_type.title())

    return {
        "report_type": report_type,
        "charts": charts,
        "summary": f"Processed as {report_type} report." if report_type != "unknown" else "Could not classify report."
    }
