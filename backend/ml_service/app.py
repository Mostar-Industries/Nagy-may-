import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_service.models.yolo_detector import YOLODetector
from ml_service.utils.image_processor import ImageProcessor
from ml_service.utils.risk_scorer import RiskScorer
from ml_service.utils.clinical_data_loader import ClinicalDataLoader
from ml_service.utils.sormas_parser import SORMASParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
yolo_detector: Optional[YOLODetector] = None
risk_scorer: Optional[RiskScorer] = None
clinical_loader: Optional[ClinicalDataLoader] = None
sormas_parser: Optional[SORMASParser] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for app startup/shutdown"""
    global yolo_detector, risk_scorer, clinical_loader, sormas_parser
    
    logger.info("[v0] Loading YOLO model and risk scorer on startup...")
    try:
        yolo_detector = YOLODetector()
        risk_scorer = RiskScorer()
        clinical_loader = ClinicalDataLoader()
        sormas_parser = SORMASParser()
        logger.info("[v0] Models and data loaded successfully")
    except Exception as e:
        logger.error(f"[v0] Failed to load models: {e}")
        raise
    
    yield
    
    logger.info("[v0] Cleaning up resources on shutdown...")
    if yolo_detector:
        yolo_detector.cleanup()


app = FastAPI(
    title="Mastomys YOLO Detection Service",
    description="ML backend for Mastomys rodent detection using YOLOv8",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DetectionResponse(BaseModel):
    """Response model for detection results"""
    success: bool
    detections: list
    risk_score: float
    processing_time_ms: float
    model_version: str
    metadata: dict


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_version: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if yolo_detector else "unhealthy",
        "model_loaded": yolo_detector is not None,
        "model_version": "yolov8n" if yolo_detector else "none"
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect(file: UploadFile = File(...)):
    """
    Detect Mastomys in uploaded image
    
    Parameters:
    - file: Image file (JPG, PNG, etc.)
    
    Returns:
    - Bounding boxes, confidence scores, and risk assessment
    """
    if not yolo_detector:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        logger.info(f"[v0] Processing image: {file.filename}")
        
        # Read and process image
        contents = await file.read()
        image_processor = ImageProcessor()
        image = image_processor.load_image_from_bytes(contents)
        
        # Run YOLO inference
        detections = yolo_detector.predict(image)
        
        # Score risk level based on detections
        risk_score = risk_scorer.score_detections(detections)
        
        # Format response
        response = {
            "success": True,
            "detections": detections,
            "risk_score": risk_score,
            "processing_time_ms": 0,  # Will be calculated in detector
            "model_version": yolo_detector.model_version,  # Use actual model version
            "metadata": {
                "filename": file.filename,
                "detection_count": len(detections),
                "high_confidence": sum(1 for d in detections if d.get("confidence", 0) > 0.7),
                "species_detected": list(set(d.get("class_name", "unknown") for d in detections))
            }
        }
        
        logger.info(f"[v0] Detection complete: {len(detections)} objects found")
        return response
        
    except Exception as e:
        logger.error(f"[v0] Detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post("/detect/batch")
async def detect_batch(files: list[UploadFile] = File(...)):
    """
    Batch detect Mastomys in multiple images
    
    Parameters:
    - files: List of image files
    
    Returns:
    - List of detection results
    """
    if not yolo_detector:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    for file in files:
        try:
            contents = await file.read()
            image_processor = ImageProcessor()
            image = image_processor.load_image_from_bytes(contents)
            detections = yolo_detector.predict(image)
            risk_score = risk_scorer.score_detections(detections)
            
            results.append({
                "filename": file.filename,
                "success": True,
                "detections": detections,
                "risk_score": risk_score
            })
        except Exception as e:
            logger.error(f"[v0] Batch error on {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {"results": results}


@app.get("/model/info")
async def model_info():
    """Get model information"""
    if not yolo_detector:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_name": "YOLOv8 Nano",
        "version": "yolov8n",
        "task": "detection",
        "classes": ["mastomys", "other-rodent", "background"],
        "input_size": 640,
        "framework": "PyTorch"
    }


@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "Mastomys YOLO Detection Service",
        "version": "0.1.0",
        "status": "ready",
        "endpoints": {
            "health": "/health",
            "detect": "/detect (POST)",
            "batch_detect": "/detect/batch (POST)",
            "model_info": "/model/info",
            "docs": "/docs",
            "clinical_cases_region": "/clinical/cases/region/{region}",
            "clinical_cases_recent": "/clinical/cases/recent",
            "clinical_statistics": "/clinical/statistics",
            "clinical_correlate": "/clinical/correlate",
            "sormas_fields": "/sormas/fields",
            "sormas_field_definition": "/sormas/field/{field_name}"
        }
    }

# New clinical data endpoints
@app.get("/clinical/cases/region/{region}")
async def get_cases_by_region(region: str):
    """Get Lassa Fever cases for a specific region"""
    if not clinical_loader:
        raise HTTPException(status_code=503, detail="Clinical data not loaded")
    
    cases = clinical_loader.get_cases_by_region(region)
    return {"region": region, "case_count": len(cases), "cases": cases}


@app.get("/clinical/cases/recent")
async def get_recent_cases(limit: int = 10):
    """Get most recent Lassa Fever cases"""
    if not clinical_loader:
        raise HTTPException(status_code=503, detail="Clinical data not loaded")
    
    cases = clinical_loader.get_recent_cases(limit)
    return {"count": len(cases), "cases": cases}


@app.get("/clinical/statistics")
async def get_clinical_statistics():
    """Get overall clinical statistics"""
    if not clinical_loader:
        raise HTTPException(status_code=503, detail="Clinical data not loaded")
    
    stats = clinical_loader.get_case_statistics()
    return stats


@app.post("/clinical/correlate")
async def correlate_detection(latitude: float, longitude: float, radius_km: float = 50):
    """Correlate rodent detection with nearby Lassa cases"""
    if not clinical_loader:
        raise HTTPException(status_code=503, detail="Clinical data not loaded")
    
    correlation = clinical_loader.correlate_detection_with_cases(latitude, longitude, radius_km)
    return correlation


@app.get("/sormas/fields")
async def get_sormas_fields():
    """Get all SORMAS data dictionary fields"""
    if not sormas_parser:
        raise HTTPException(status_code=503, detail="SORMAS parser not loaded")
    
    fields = sormas_parser.get_all_fields()
    return {"field_count": len(fields), "fields": fields}


@app.get("/sormas/field/{field_name}")
async def get_sormas_field_definition(field_name: str):
    """Get definition for a specific SORMAS field"""
    if not sormas_parser:
        raise HTTPException(status_code=503, detail="SORMAS parser not loaded")
    
    definition = sormas_parser.get_field_definition(field_name)
    if definition:
        return definition
    raise HTTPException(status_code=404, detail="Field not found")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"[v0] Starting ML service on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
