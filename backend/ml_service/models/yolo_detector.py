import logging
import time
import os
from typing import List, Dict, Any
import numpy as np
from ultralytics import YOLO
from PIL import Image

logger = logging.getLogger(__name__)


class YOLODetector:
    """YOLOv8 detector for Mastomys natalensis identification - Production Version"""
    
    # Class mapping from training (matches your Kaggle training output)
    CLASS_NAMES = {
        0: "Natal-Multimammate-Mouse",  # Mastomys natalensis
        1: "Rattus-rattus",              # Black rat (if in dataset)
        2: "Other-rodent"                # Catch-all
    }
    
    SPECIES_MAP = {
        0: "Mastomys natalensis",
        1: "Rattus rattus", 
        2: "Other rodent"
    }
    
    # Lassa fever risk weights by species
    LASSA_RISK_WEIGHTS = {
        0: 1.0,   # Mastomys natalensis - primary reservoir
        1: 0.3,   # Rattus rattus - low risk
        2: 0.1    # Other - minimal risk
    }

    def __init__(self, model_path: str = None, device: str = None):
        """
        Initialize YOLO detector with production weights
        
        Args:
            model_path: Path to trained model weights (best.pt)
            device: Device to run on ('cpu', 'cuda', or 'mps')
        """
        self.device = device or os.getenv("YOLO_DEVICE", "cpu")
        self.confidence_threshold = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.5"))
        
        # Model path resolution order:
        # 1. Explicit path passed in
        # 2. Environment variable
        # 3. Default location in weights folder
        # 4. Legacy "model/weights" folder (if used)
        candidate_paths = []
        if model_path:
            candidate_paths.append(model_path)
        env_model_path = os.getenv("YOLO_MODEL_PATH")
        if env_model_path:
            candidate_paths.append(env_model_path)

        default_path = os.path.join(os.path.dirname(__file__), "weights", "best.pt")
        legacy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model", "weights", "best.pt")
        candidate_paths.extend([default_path, legacy_path])

        self.model_path = next(
            (path for path in candidate_paths if path and os.path.exists(path)),
            candidate_paths[0] if candidate_paths else default_path
        )

        if self.model_path == legacy_path:
            logger.warning("[v2] Using legacy model path: %s", legacy_path)
        
        logger.info(f"[v2] Initializing YOLODetector")
        logger.info(f"[v2] Model path: {self.model_path}")
        logger.info(f"[v2] Device: {self.device}")
        logger.info(f"[v2] Confidence threshold: {self.confidence_threshold}")
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model with fallback logic"""
        try:
            if os.path.exists(self.model_path):
                logger.info(f"[v2] Loading production model from {self.model_path}")
                self.model = YOLO(self.model_path)
                self.model_version = "yolov8s-mastomys-production-v2"
                self.model_metrics = {
                    "mAP50": 0.726,
                    "mAP50-95": 0.391,
                    "precision": 0.908,
                    "recall": 0.714
                }
            else:
                logger.warning(f"[v2] Production model not found at {self.model_path}")
                logger.warning("[v2] Falling back to base YOLOv8s model")
                self.model = YOLO("yolov8s.pt")
                self.model_version = "yolov8s-base-fallback"
                self.model_metrics = {}
            
            self.model.to(self.device)
            logger.info(f"[v2] Model loaded successfully: {self.model_version}")
            
        except Exception as e:
            logger.error(f"[v2] Failed to load YOLO model: {e}")
            raise RuntimeError(f"Model initialization failed: {e}")
    
    def predict(self, image: Image.Image, conf_threshold: float = None) -> List[Dict[str, Any]]:
        """
        Run inference on image
        
        Args:
            image: PIL Image object
            conf_threshold: Confidence threshold (uses default if not specified)
        
        Returns:
            List of detection dictionaries with bbox, confidence, class, species, risk
        """
        conf = conf_threshold or self.confidence_threshold
        start_time = time.time()
        
        try:
            # Run inference
            results = self.model(image, conf=conf, verbose=False)
            
            # Parse results
            detections = []
            for result in results:
                boxes = result.boxes
                
                for i, box in enumerate(boxes):
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Get coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # Calculate Lassa risk contribution for this detection
                    lassa_risk_weight = self.LASSA_RISK_WEIGHTS.get(class_id, 0.1)
                    detection_risk = confidence * lassa_risk_weight
                    
                    detection = {
                        "id": i,
                        "bbox": {
                            "x": float(x1),
                            "y": float(y1),
                            "width": float(x2 - x1),
                            "height": float(y2 - y1),
                            "x_center": float((x1 + x2) / 2),
                            "y_center": float((y1 + y2) / 2),
                        },
                        "confidence": round(confidence, 4),
                        "class_id": class_id,
                        "class_name": result.names.get(class_id, self.CLASS_NAMES.get(class_id, "unknown")),
                        "species": self.SPECIES_MAP.get(class_id, "Unknown"),
                        "species_confidence": round(confidence, 4),
                        "lassa_risk_weight": lassa_risk_weight,
                        "detection_risk_score": round(detection_risk, 4),
                        "is_primary_reservoir": class_id == 0,  # Mastomys natalensis
                    }
                    detections.append(detection)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Add timing and model info to each detection
            for detection in detections:
                detection["processing_time_ms"] = round(processing_time, 2)
                detection["model_version"] = self.model_version
            
            logger.info(f"[v2] Inference: {len(detections)} detections in {processing_time:.2f}ms")
            
            # Log Mastomys-specific findings
            mastomys_count = sum(1 for d in detections if d["is_primary_reservoir"])
            if mastomys_count > 0:
                logger.info(f"[v2] âš ï¸ ALERT: {mastomys_count} Mastomys natalensis detected!")
            
            return detections
            
        except Exception as e:
            logger.error(f"[v2] Inference error: {e}", exc_info=True)
            raise
    
    def predict_batch(self, images: List[Image.Image], conf_threshold: float = None) -> List[List[Dict[str, Any]]]:
        """
        Run batch inference on multiple images
        
        Args:
            images: List of PIL Image objects
            conf_threshold: Confidence threshold
        
        Returns:
            List of detection lists, one per image
        """
        return [self.predict(img, conf_threshold) for img in images]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata"""
        return {
            "model_name": "YOLOv8s Mastomys Detector",
            "version": self.model_version,
            "model_path": self.model_path,
            "device": self.device,
            "confidence_threshold": self.confidence_threshold,
            "task": "detection",
            "classes": list(self.CLASS_NAMES.values()),
            "num_classes": len(self.CLASS_NAMES),
            "input_size": 640,
            "framework": "PyTorch/Ultralytics",
            "metrics": self.model_metrics,
            "primary_target": "Mastomys natalensis (Lassa fever reservoir)",
        }
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("[v2] Cleaning up YOLO detector")
        if hasattr(self, 'model'):
            del self.model

