import logging
import cv2
import numpy as np
from typing import Dict, Optional, List
logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    import torch
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    logger.warning("[INFERENCE] Ultralytics or Torch not found. Falling back to Mock Mode.")
    ULTRALYTICS_AVAILABLE = False

class InferenceEngine:
    """
    Local inference engine using Ultralytics YOLO.
    Eliminates the need for external API calls for detection.
    """
    
    def __init__(self, model_path: str, conf_threshold: float = 0.5):
        """
        Initialize the inference engine.
        
        Args:
            model_path: Path to the .pt model file
            conf_threshold: Minimum confidence score for detections
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.model = None
        self.device = 'cuda' if (ULTRALYTICS_AVAILABLE and torch.cuda.is_available()) else 'cpu'
        
        self._load_model()
        
    def _load_model(self):
        """Load the YOLO model within safety blocks"""
        if not ULTRALYTICS_AVAILABLE:
            logger.warning("[INFERENCE] Skipping real model load (Mock Mode enabled)")
            return

        try:
            logger.info(f"[INFERENCE] Loading model from {self.model_path} on {self.device}...")
            self.model = YOLO(self.model_path)
            logger.info(f"[INFERENCE] Model loaded successfully")
        except Exception as e:
            logger.error(f"[INFERENCE] Failed to load model: {e}")
            logger.warning("[INFERENCE] Transitioning to Mock Mode fallback")

    def predict(self, frame: np.ndarray) -> Optional[Dict]:
        """Run inference on a single frame."""
        if not ULTRALYTICS_AVAILABLE or self.model is None:
            # Generate a mock detection for verification
            logger.debug("[INFERENCE] Generating mock detection (natalensis)")
            return {
                "detections": [{
                    "bbox": [100.0, 100.0, 200.0, 200.0],
                    "confidence": 0.88,
                    "class": "Mastomys_natalensis",
                    "class_id": 0
                }],
                "count": 1,
                "avg_confidence": 0.88,
                "inference_time": 5.0,
                "is_mock": True
            }
            
        try:
            # Run inference
            # stream=True for efficiency if processing video frames sequentially, 
            # but for single frame calls, standard predict is fine.
            results = self.model.predict(
                source=frame, 
                conf=self.conf_threshold, 
                device=self.device, 
                verbose=False
            )
            
            # Process results
            # YOLO results is a list (one per image), we only sent one
            result = results[0]
            
            detections = []
            total_conf = 0
            
            for box in result.boxes:
                # Extract box coordinates (xyxy)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                class_name = self.model.names[cls_id]
                
                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": conf,
                    "class": class_name,
                    "class_id": cls_id
                })
                total_conf += conf
                
            avg_conf = (total_conf / len(detections)) if detections else 0.0
            
            return {
                "detections": detections,
                "count": len(detections),
                "avg_confidence": avg_conf,
                "inference_time": sum(result.speed.values()) # sum of pre, inference, post in ms
            }
            
        except Exception as e:
            logger.error(f"[INFERENCE] Inference error: {e}")
            return None
