import logging
import time
import os
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
        self.model_version = "yolov8s-trained"  # Track model version
        
        try:
            trained_model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "mntrk-tensorflow2-symbolic-v2",
                "results234",
                "yolov8s.pt"
            )
            
            if os.path.exists(trained_model_path):
                logger.info(f"[v0] Loading trained model from {trained_model_path}")
                self.model = YOLO(trained_model_path)
                self.model_version = "yolov8s-trained-mastomys"
            else:
                logger.warning(f"[v0] Trained model not found, falling back to {model_name}")
                self.model = YOLO(model_name)
                self.model_version = model_name
            
            self.model.to(device)
            logger.info(f"[v0] Model loaded successfully: {self.model_version}")
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
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Species mapping for YOLO classes
                    species_map = {
                        0: "Mastomys natalensis",
                        1: "Mastomys coucha",
                        2: "Other rodent",
                        3: "Unknown"
                    }
                    
                    detection = {
                        "id": i,
                        "bbox": {
                            "x": float(box.xyxy[0][0]),
                            "y": float(box.xyxy[0][1]),
                            "width": float(box.xyxy[0][2] - box.xyxy[0][0]),
                            "height": float(box.xyxy[0][3] - box.xyxy[0][1]),
                        },
                        "confidence": confidence,
                        "class": class_id,
                        "class_name": result.names.get(class_id, "unknown"),
                        "species": species_map.get(class_id, "Unknown"),
                        "species_confidence": confidence,
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
