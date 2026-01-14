import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import time
from datetime import datetime
import httpx

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_service.models.yolo_detector import YOLODetector
from ml_service.utils.image_processor import ImageProcessor
from ml_service.utils.risk_scorer import RiskScorer
from ml_service.utils.clinical_data_loader import ClinicalDataLoader
from ml_service.utils.sormas_parser import SORMASParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
yolo_detector: Optional[YOLODetector] = None
risk_scorer: Optional[RiskScorer] = None
clinical_loader: Optional[ClinicalDataLoader] = None
sormas_parser: Optional[SORMASParser] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for app startup/shutdown"""
    global yolo_detector, risk_scorer, clinical_loader, sormas_parser
    
    logger.info("[v2] ====== SKYHAWK ML SERVICE STARTING ======")
    logger.info("[v2] Loading production Mastomys detection model...")
    
    try:
        # Initialize YOLO detector with production weights
        yolo_detector = YOLODetector()
        risk_scorer = RiskScorer()
        
        # Optional data loaders (graceful failure)
        try:
            clinical_loader = ClinicalDataLoader()
            logger.info("[v2] Clinical data loader initialized")
        except Exception as e:
            logger.warning(f"[v2] Clinical data loader unavailable: {e}")
            clinical_loader = None
        
        try:
            sormas_parser = SORMASParser()
            logger.info("[v2] SORMAS parser initialized")
        except Exception as e:
            logger.warning(f"[v2] SORMAS parser unavailable: {e}")
            sormas_parser = None
        
        logger.info("[v2] ====== ML SERVICE READY ======")
        logger.info(f"[v2] Model: {yolo_detector.model_version}")
        logger.info(f"[v2] Device: {yolo_detector.device}")
        
    except Exception as e:
        logger.error(f"[v2] CRITICAL: Failed to load models: {e}")
        raise
    
    yield
    
    logger.info("[v2] Shutting down ML service...")
    if yolo_detector:
        yolo_detector.cleanup()
    logger.info("[v2] Cleanup complete")


app = FastAPI(
    title="Skyhawk Mastomys Detection Service",
    description="""
    Production ML backend for Mastomys natalensis detection using YOLOv8.
    
    Part of the Skyhawk health surveillance system for Lassa fever prevention.
    
    **Key Features:**
    - Real-time rodent detection with 90.8% precision
    - Lassa fever risk scoring based on species identification
    - Clinical data correlation for outbreak prediction
    - SORMAS integration for epidemiological analysis
    
    **Model Performance (v2 Production):**
    - mAP@50: 72.6%
    - mAP@50-95: 39.1%
    - Precision: 90.8%
    - Recall: 71.4%
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== RESPONSE MODELS ====================

class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float
    x_center: float
    y_center: float


class Detection(BaseModel):
    id: int
    bbox: BoundingBox
    confidence: float
    class_id: int
    class_name: str
    species: str
    species_confidence: float
    lassa_risk_weight: float
    detection_risk_score: float
    is_primary_reservoir: bool
    processing_time_ms: float
    model_version: str


class DetectionResponse(BaseModel):
    success: bool
    detections: List[Detection]
    risk_score: float
    risk_level: str
    processing_time_ms: float
    model_version: str
    metadata: dict
    timestamp: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    remostar_analysis: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    device: str
    uptime_seconds: float = Field(default=0)


class ModelInfoResponse(BaseModel):
    model_name: str
    version: str
    model_path: str
    device: str
    confidence_threshold: float
    task: str
    classes: List[str]
    num_classes: int
    input_size: int
    framework: str
    metrics: dict
    primary_target: str


# Track uptime
_start_time = time.time()


def _remostar_endpoint() -> str:
    base = os.getenv("REMOSTAR_API_URL", "http://localhost:7777").rstrip("/")
    if base.endswith("/analyze"):
        return base
    return f"{base}/analyze"


async def _call_remostar(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(_remostar_endpoint(), json=payload)
            if response.status_code >= 400:
                logger.warning(f"[v2] REMOSTAR error: {response.status_code} {response.text}")
                return None
            return response.json()
    except Exception as e:
        logger.warning(f"[v2] REMOSTAR unavailable: {e}")
        return None


# ==================== ENDPOINTS ====================

@app.get("/", tags=["Info"])
async def root():
    """API documentation and endpoint overview"""
    return {
        "name": "Skyhawk Mastomys Detection Service",
        "version": "2.0.0",
        "status": "ready" if yolo_detector else "initializing",
        "model": yolo_detector.model_version if yolo_detector else "loading",
        "endpoints": {
            "health": "GET /health",
            "detect": "POST /detect",
            "detect_batch": "POST /detect/batch",
            "model_info": "GET /model/info",
            "docs": "GET /docs",
            "clinical_cases_region": "GET /clinical/cases/region/{region}",
            "clinical_cases_recent": "GET /clinical/cases/recent",
            "clinical_statistics": "GET /clinical/statistics",
            "clinical_correlate": "POST /clinical/correlate",
            "sormas_fields": "GET /sormas/fields",
            "sormas_field": "GET /sormas/field/{field_name}"
        },
        "mostar_industries": {
            "project": "Lassa Shield",
            "initiative": "African Flame Initiative",
            "mission": "Health surveillance through African technological sovereignty"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Service health check with model status"""
    return {
        "status": "healthy" if yolo_detector else "unhealthy",
        "model_loaded": yolo_detector is not None,
        "model_version": yolo_detector.model_version if yolo_detector else "none",
        "device": yolo_detector.device if yolo_detector else "none",
        "uptime_seconds": round(time.time() - _start_time, 2)
    }


@app.post("/detect", response_model=DetectionResponse, tags=["Detection"])
async def detect(
    file: UploadFile = File(...),
    confidence: float = Query(default=0.5, ge=0.1, le=1.0, description="Confidence threshold"),
    latitude: Optional[float] = Form(default=None),
    longitude: Optional[float] = Form(default=None),
    enhance_with_remostar: Optional[bool] = Form(default=False),
):
    """
    Detect Mastomys in uploaded image
    
    - **file**: Image file (JPG, PNG, WEBP)
    - **confidence**: Detection confidence threshold (0.1-1.0)
    
    Returns bounding boxes, species identification, and Lassa fever risk assessment.
    """
    if not yolo_detector:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    start_time = time.time()
    
    try:
        logger.info(f"[v2] Processing: {file.filename}")
        
        # Read and process image
        contents = await file.read()
        image_processor = ImageProcessor()
        image = image_processor.load_image_from_bytes(contents)
        
        # Run YOLO inference
        detections = yolo_detector.predict(image, conf_threshold=confidence)
        
        # Calculate aggregate risk score
        risk_score = risk_scorer.score_detections(detections)
        risk_level = _get_risk_level(risk_score)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Count Mastomys specifically
        mastomys_count = sum(1 for d in detections if d.get("is_primary_reservoir", False))
        high_conf_count = sum(1 for d in detections if d.get("confidence", 0) > 0.7)
        
        timestamp = datetime.utcnow().isoformat()
        location = None
        if latitude is not None and longitude is not None:
            location = {"latitude": latitude, "longitude": longitude}

        response = {
            "success": True,
            "detections": detections,
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "processing_time_ms": round(processing_time, 2),
            "model_version": yolo_detector.model_version,
            "timestamp": timestamp,
            "location": location,
            "metadata": {
                "filename": file.filename,
                "detection_count": len(detections),
                "mastomys_count": mastomys_count,
                "high_confidence_count": high_conf_count,
                "species_detected": list(set(d.get("species", "unknown") for d in detections)),
                "lassa_reservoir_detected": mastomys_count > 0,
                "confidence_threshold_used": confidence
            }
        }

        if enhance_with_remostar:
            remostar_payload = {
                "timestamp": timestamp,
                "source_id": "ml_service",
                "location": location or {},
                "detections": [
                    {"species": d.get("species"), "confidence": d.get("confidence"), "bbox": d.get("bbox")}
                    for d in detections
                ],
            }
            response["remostar_analysis"] = await _call_remostar(remostar_payload)
        
        # Log alert for Mastomys detection
        if mastomys_count > 0:
            logger.warning(f"[v2] 🚨 LASSA RISK: {mastomys_count} Mastomys natalensis in {file.filename}")
        
        logger.info(f"[v2] Complete: {len(detections)} detections, risk={risk_level}")
        return response
        
    except Exception as e:
        logger.error(f"[v2] Detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post("/detect/batch", tags=["Detection"])
async def detect_batch(
    files: List[UploadFile] = File(...),
    confidence: float = Query(default=0.5, ge=0.1, le=1.0)
):
    """
    Batch detect Mastomys in multiple images
    
    Returns detection results for each image with aggregate statistics.
    """
    if not yolo_detector:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    total_mastomys = 0
    
    for file in files:
        try:
            contents = await file.read()
            image_processor = ImageProcessor()
            image = image_processor.load_image_from_bytes(contents)
            detections = yolo_detector.predict(image, conf_threshold=confidence)
            risk_score = risk_scorer.score_detections(detections)
            
            mastomys_count = sum(1 for d in detections if d.get("is_primary_reservoir", False))
            total_mastomys += mastomys_count
            
            results.append({
                "filename": file.filename,
                "success": True,
                "detections": detections,
                "detection_count": len(detections),
                "mastomys_count": mastomys_count,
                "risk_score": round(risk_score, 4),
                "risk_level": _get_risk_level(risk_score)
            })
        except Exception as e:
            logger.error(f"[v2] Batch error on {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {
        "results": results,
        "summary": {
            "total_files": len(files),
            "successful": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success")),
            "total_detections": sum(r.get("detection_count", 0) for r in results if r.get("success")),
            "total_mastomys": total_mastomys,
            "lassa_alert": total_mastomys > 0
        }
    }


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def model_info():
    """Get detailed model information and performance metrics"""
    if not yolo_detector:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return yolo_detector.get_model_info()


# ==================== CLINICAL ENDPOINTS ====================

@app.get("/clinical/cases/region/{region}", tags=["Clinical"])
async def get_cases_by_region(region: str):
    """Get Lassa Fever cases for a specific region"""
    if not clinical_loader:
        raise HTTPException(status_code=503, detail="Clinical data not loaded")
    
    cases = clinical_loader.get_cases_by_region(region)
    return {"region": region, "case_count": len(cases), "cases": cases}


@app.get("/clinical/cases/recent", tags=["Clinical"])
async def get_recent_cases(limit: int = Query(default=10, ge=1, le=100)):
    """Get most recent Lassa Fever cases"""
    if not clinical_loader:
        raise HTTPException(status_code=503, detail="Clinical data not loaded")
    
    cases = clinical_loader.get_recent_cases(limit)
    return {"count": len(cases), "cases": cases}


@app.get("/clinical/statistics", tags=["Clinical"])
async def get_clinical_statistics():
    """Get overall clinical statistics"""
    if not clinical_loader:
        raise HTTPException(status_code=503, detail="Clinical data not loaded")
    
    return clinical_loader.get_case_statistics()


@app.post("/clinical/correlate", tags=["Clinical"])
async def correlate_detection(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=50, ge=1, le=500)
):
    """Correlate rodent detection with nearby Lassa cases"""
    if not clinical_loader:
        raise HTTPException(status_code=503, detail="Clinical data not loaded")
    
    correlation = clinical_loader.correlate_detection_with_cases(latitude, longitude, radius_km)
    return correlation


# ==================== SORMAS ENDPOINTS ====================

@app.get("/sormas/fields", tags=["SORMAS"])
async def get_sormas_fields():
    """Get all SORMAS data dictionary fields"""
    if not sormas_parser:
        raise HTTPException(status_code=503, detail="SORMAS parser not loaded")
    
    fields = sormas_parser.get_all_fields()
    return {"field_count": len(fields), "fields": fields}


@app.get("/sormas/field/{field_name}", tags=["SORMAS"])
async def get_sormas_field_definition(field_name: str):
    """Get definition for a specific SORMAS field"""
    if not sormas_parser:
        raise HTTPException(status_code=503, detail="SORMAS parser not loaded")
    
    definition = sormas_parser.get_field_definition(field_name)
    if definition:
        return definition
    raise HTTPException(status_code=404, detail="Field not found")


# ==================== HELPERS ====================

def _get_risk_level(risk_score: float) -> str:
    """Convert risk score to categorical level"""
    if risk_score >= 0.8:
        return "CRITICAL"
    elif risk_score >= 0.6:
        return "HIGH"
    elif risk_score >= 0.4:
        return "MODERATE"
    elif risk_score >= 0.2:
        return "LOW"
    else:
        return "MINIMAL"


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "5001"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"[v2] Starting Skyhawk ML Service on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
