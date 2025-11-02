import logging
import time
from typing import List, Dict, Any
import numpy as np
from ultralytics import YOLO
from PIL import Image

logger = logging.getLogger(__name__)


class YOLODetector:
    """YOLOv8 detector for Mastomys identification"""
    
    def __init__(self, model_name: str = "yolov8n.pt", device: str = "cpu"):
        """
        Initialize YOLO detector
        
        Args:
            model_name: Model file name (yolov8n, yolov8s, yolov8m, etc.)
            device: Device to run on ('cpu' or 'cuda')
        """
        logger.info(f"[v0] Initializing YOLODetector with {model_name} on {device}")
        self.model_name = model_name
        self.device = device
        
        try:
            # Load YOLOv8 model (auto-downloads if not present)
            self.model = YOLO(model_name)
            self.model.to(device)
            logger.info(f"[v0] Model loaded successfully: {model_name}")
        except Exception as e:
            logger.error(f"[v0] Failed to load YOLO model: {e}")
            raise
    
    def predict(self, image: Image.Image, conf_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Run inference on image
        
        Args:
            image: PIL Image object
            conf_threshold: Confidence threshold for detections
        
        Returns:
            List of detection dictionaries with bbox, confidence, class
        """
        start_time = time.time()
        
        try:
            # Run inference
            results = self.model(image, conf=conf_threshold, verbose=False)
            
            # Parse results
            detections = []
            for result in results:
                boxes = result.boxes
                
                for i, box in enumerate(boxes):
                    detection = {
                        "id": i,
                        "bbox": {
                            "x": float(box.xyxy[0][0]),
                            "y": float(box.xyxy[0][1]),
                            "width": float(box.xyxy[0][2] - box.xyxy[0][0]),
                            "height": float(box.xyxy[0][3] - box.xyxy[0][1]),
                        },
                        "confidence": float(box.conf[0]),
                        "class": int(box.cls[0]),
                        "class_name": result.names.get(int(box.cls[0]), "unknown")
                    }
                    detections.append(detection)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"[v0] Inference completed in {processing_time:.2f}ms, {len(detections)} detections")
            
            # Add timing info to each detection
            for detection in detections:
                detection["processing_time_ms"] = processing_time
            
            return detections
            
        except Exception as e:
            logger.error(f"[v0] Inference error: {e}")
            raise
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("[v0] Cleaning up YOLO detector")
        if hasattr(self, 'model'):
            del self.model
