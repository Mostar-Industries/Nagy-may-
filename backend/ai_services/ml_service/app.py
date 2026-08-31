"""
Skyhawk ML Service - YOLO11n Detection with REMOSTAR Integration
Port: 5001
Authority: Species detection, confidence scoring, basic ML processing
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import sys

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
import io

# YOLO11n integration
from ultralytics import YOLO
import cv2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# REMOSTAR consciousness integration (Shared Volume)
try:
    # Add shared volume paths to sys.path
    if os.path.exists("/app/ai_services_shared"):
        sys.path.append("/app/ai_services_shared")
        sys.path.append("/app/ai_services_shared/consciousness")
    
    from remostar_integration import analyze_detection_consciousness
    CONSCIOUSNESS_AVAILABLE = True
    logger.info("[v2] Shared Remostar Consciousness Engine loaded successfully")
except ImportError as e:
    logger.warning(f"[v2] Shared Consciousness Engine not found: {e}")
    CONSCIOUSNESS_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="Skyhawk ML Service",
    description="YOLO11n Detection Service with REMOSTAR Consciousness Enhancement",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global settings
MODEL_PATH = os.getenv('YOLO_MODEL_PATH', '/app/models/weights/yolo11n.pt')
CONFIDENCE_THRESHOLD = float(os.getenv('YOLO_CONFIDENCE_THRESHOLD', '0.5'))
IOU_THRESHOLD = float(os.getenv('YOLO_IOU_THRESHOLD', '0.4'))
DEVICE = os.getenv('YOLO_DEVICE', 'cpu')

# Mastomys species mapping
MASTOMYS_SPECIES_MAP = {
    0: 'Mastomys_natalensis',      # Primary Lassa reservoir
    1: 'Mastomys_erythroleucus',   # Secondary reservoir  
    2: 'Mastomys_coucha',          # Occasional reservoir
    3: 'Mastomys_kollmannspergeri', # Rare reservoir
    4: 'Rattus_rattus',            # Common house rat
    5: 'Mus_musculus',             # House mouse
    6: 'Other_rodent'              # Unclassified rodent
}

class MLDetectionService:
    """
    Core ML Detection Service
    Authority: YOLO inference, species classification, confidence assessment
    """
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.detection_count = 0
        
    async def initialize_model(self):
        """Initialize YOLO11n model"""
        try:
            if os.path.exists(MODEL_PATH):
                logger.info(f"Loading YOLO11n model from {MODEL_PATH}")
                self.model = YOLO(MODEL_PATH)
                self.model_loaded = True
                logger.info(f"YOLO11n model loaded successfully on {DEVICE}")
            else:
                logger.warning(f"Model not found at {MODEL_PATH}, using default YOLOv8n")
                self.model = YOLO('yolov8n.pt')  # Fallback to default
                self.model_loaded = True
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model_loaded = False
    
    async def detect_objects(self, image: Image.Image, enhance_with_consciousness: bool = True) -> Dict:
        """
        Core detection function
        Authority: ML inference, species identification, confidence scoring
        """
        if not self.model_loaded:
            raise HTTPException(status_code=503, detail="ML model not available")
        
        try:
            # Convert PIL to numpy array for YOLO
            img_array = np.array(image)
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:  # RGBA
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            
            # Run YOLO inference
            results = self.model(
                img_array,
                conf=CONFIDENCE_THRESHOLD,
                iou=IOU_THRESHOLD,
                device=DEVICE,
                verbose=False
            )
            
            # Process detections
            detections = []
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                
                for i, box in enumerate(boxes):
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    # Map class ID to species
                    species = MASTOMYS_SPECIES_MAP.get(class_id, 'Unknown_rodent')
                    
                    detection = {
                        'detection_id': f"det_{self.detection_count}_{i}",
                        'species': species,
                        'confidence': round(confidence, 4),
                        'bbox': {
                            'x1': round(bbox[0], 2),
                            'y1': round(bbox[1], 2), 
                            'x2': round(bbox[2], 2),
                            'y2': round(bbox[3], 2)
                        },
                        'class_id': class_id,
                        'risk_priority': self._assess_species_risk_priority(species, confidence)
                    }
                    detections.append(detection)
            
            self.detection_count += 1
            
            # Build ML response
            ml_response = {
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat(),
                'model_info': {
                    'model_type': 'yolo11n',
                    'model_version': '11.0.0',
                    'confidence_threshold': CONFIDENCE_THRESHOLD,
                    'iou_threshold': IOU_THRESHOLD,
                    'device': DEVICE
                },
                'detections': detections,
                'status_code': 200,
                'detection_summary': {
                    'total_detections': len(detections),
                    'species_detected': list(set([d['species'] for d in detections])),
                    'max_confidence': max([d['confidence'] for d in detections]) if detections else 0.0,
                    'high_risk_detections': len([d for d in detections if d['risk_priority'] == 'high'])
                }
            }
            
            # Enhanced consciousness analysis (if available and requested)
            if enhance_with_consciousness and CONSCIOUSNESS_AVAILABLE and detections:
                try:
                    # Enrich detection data with location before analysis for better persistence
                    analysis_context = {
                        'detections': detections,
                        'timestamp': ml_response['timestamp']
                    }
                    if latitude is not None and longitude is not None:
                        analysis_context['location'] = {'latitude': latitude, 'longitude': longitude}
                    
                    consciousness_analysis = analyze_detection_consciousness(
                        detection_data=analysis_context
                    )
                    ml_response['consciousness_enhancement'] = consciousness_analysis
                    ml_response['enhanced_by'] = 'remostar_consciousness'
                except Exception as e:
                    logger.warning(f"Consciousness enhancement failed: {e}")
                    ml_response['consciousness_enhancement'] = {
                        'status': 'consciousness_unavailable',
                        'error': str(e)
                    }
            
            return ml_response
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            raise HTTPException(status_code=500, detail=f"Detection processing failed: {str(e)}")
    
    def _assess_species_risk_priority(self, species: str, confidence: float) -> str:
        """Assess risk priority based on species and confidence"""
        if species == 'Mastomys_natalensis' and confidence > 0.8:
            return 'critical'
        elif species in ['Mastomys_natalensis', 'Mastomys_erythroleucus'] and confidence > 0.6:
            return 'high'
        elif 'Mastomys' in species and confidence > 0.5:
            return 'medium'
        else:
            return 'low'

# Global service instance
detection_service = MLDetectionService()

@app.on_event("startup")
async def startup_event():
    """Initialize the ML service on startup"""
    logger.info("Starting Skyhawk ML Service...")
    await detection_service.initialize_model()
    logger.info(f"ML Service ready - Model loaded: {detection_service.model_loaded}")

@app.post("/detect")
async def detect_mastomys(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    source_id: Optional[str] = Form("ml_service_upload"),
    enhance_with_remostar: Optional[bool] = Form(True)
):
    """
    Main detection endpoint
    Authority: ML detection processing, species classification, response formatting
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and validate image
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        try:
            image = Image.open(io.BytesIO(contents))
            if image.mode in ['RGBA', 'LA']:
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {e}")
        
        # Log detection request
        logger.info(f"Processing detection request: {file.filename}, Source: {source_id}")
        
        # Run detection
        detection_result = await detection_service.detect_objects(
            image, 
            enhance_with_consciousness=enhance_with_remostar
        )
        
        # Add location data if provided
        if latitude is not None and longitude is not None:
            detection_result['location'] = {
                'latitude': latitude,
                'longitude': longitude,
                'location_source': 'upload_metadata'
            }
        
        detection_result['source_info'] = {
            'source_id': source_id,
            'filename': file.filename,
            'file_size': len(contents),
            'content_type': file.content_type
        }
        
        # Log successful detection
        species_count = len(detection_result['detection_summary']['species_detected'])
        logger.info(f"Detection complete: {species_count} species detected")
        
        return JSONResponse(content=detection_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in detection endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'model_loaded': detection_service.model_loaded,
        'model_path': MODEL_PATH,
        'device': DEVICE,
        'consciousness_available': CONSCIOUSNESS_AVAILABLE,
        'detections_processed': detection_service.detection_count,
        'timestamp': datetime.utcnow().isoformat()
    }

@app.get("/model/info")
async def model_info():
    """Model information endpoint"""
    if not detection_service.model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        'model_type': 'yolo11n',
        'model_path': MODEL_PATH,
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'iou_threshold': IOU_THRESHOLD,
        'device': DEVICE,
        'species_classes': MASTOMYS_SPECIES_MAP,
        'consciousness_integration': CONSCIOUSNESS_AVAILABLE
    }

@app.post("/detect/batch")
async def batch_detect(files: List[UploadFile] = File(...)):
    """Batch detection endpoint for multiple images"""
    if len(files) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 10 images per batch")
    
    results = []
    
    for i, file in enumerate(files):
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            if image.mode in ['RGBA', 'LA']:
                image = image.convert('RGB')
            
            detection_result = await detection_service.detect_objects(image, enhance_with_consciousness=False)
            detection_result['batch_index'] = i
            detection_result['filename'] = file.filename
            results.append(detection_result)
            
        except Exception as e:
            results.append({
                'batch_index': i,
                'filename': file.filename,
                'error': str(e),
                'status': 'failed'
            })
    
    return {
        'batch_results': results,
        'total_files': len(files),
        'successful_detections': len([r for r in results if 'error' not in r]),
        'timestamp': datetime.utcnow().isoformat()
    }

# Mock responses for testing consciousness layers
@app.post("/mock/detect")
async def mock_detection_for_testing(
    species: str = Form("Mastomys_natalensis"),
    confidence: float = Form(0.85),
    num_detections: int = Form(1)
):
    """
    Mock detection endpoint for testing consciousness layers
    Returns realistic detection data without requiring real images
    """
    mock_detections = []
    
    for i in range(num_detections):
        mock_detection = {
            'detection_id': f"mock_det_{i}",
            'species': species,
            'confidence': round(confidence - (i * 0.05), 4),  # Slightly decrease confidence for each detection
            'bbox': {
                'x1': 100 + (i * 50),
                'y1': 150 + (i * 30), 
                'x2': 200 + (i * 50),
                'y2': 250 + (i * 30)
            },
            'class_id': 0 if 'natalensis' in species else 1,
            'risk_priority': 'high' if 'natalensis' in species and confidence > 0.8 else 'medium'
        }
        mock_detections.append(mock_detection)
    
    mock_response = {
        'status': 'mock_success',
        'timestamp': datetime.utcnow().isoformat(),
        'model_info': {
            'model_type': 'mock_yolo11n',
            'model_version': 'testing',
            'confidence_threshold': CONFIDENCE_THRESHOLD,
            'device': 'mock_device'
        },
        'detections': mock_detections,
        'detection_summary': {
            'total_detections': len(mock_detections),
            'species_detected': [species],
            'max_confidence': confidence,
            'high_risk_detections': len([d for d in mock_detections if d['risk_priority'] == 'high'])
        }
    }
    
    # Apply consciousness enhancement to mock data
    if CONSCIOUSNESS_AVAILABLE:
        try:
            consciousness_analysis = analyze_detection_consciousness(
                detection_data={
                    'detections': mock_detections,
                    'timestamp': mock_response['timestamp']
                }
            )
            mock_response['consciousness_enhancement'] = consciousness_analysis
            mock_response['enhanced_by'] = 'remostar_consciousness_mock'
        except Exception as e:
            logger.warning(f"Mock consciousness enhancement failed: {e}")
    
    return JSONResponse(content=mock_response)

if __name__ == "__main__":
    # Run the service
    port = int(os.getenv('PORT', '5001'))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting ML Service on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
