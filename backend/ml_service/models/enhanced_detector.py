import logging
import time
from typing import List, Dict, Any, Optional
import numpy as np
from ultralytics import YOLO
from PIL import Image
import cv2

logger = logging.getLogger(__name__)


class EnhancedMastomysDetector:
    """Enhanced YOLO detector with multi-classification for detailed tracking"""
    
    # Detection type classification based on proximity and count
    DETECTION_TYPES = {
        'single': 1,
        'pair': 2,
        'group': (3, 5),
        'colony': 6
    }
    
    # Species classification
    SPECIES_MAP = {
        0: "Mastomys natalensis",
        1: "Mastomys coucha",
        2: "Mastomys erythroleucus",
        3: "Rattus rattus",
        4: "Mus musculus",
        5: "Other rodent"
    }
    
    # Gender indicators (based on visual features)
    GENDER_INDICATORS = ['male', 'female', 'unknown']
    
    # Age estimation categories
    AGE_CATEGORIES = ['juvenile', 'young_adult', 'adult', 'elderly']
    
    # Health status indicators
    HEALTH_STATUS = ['healthy', 'sick', 'injured', 'deceased']
    
    def __init__(self, 
                 detection_model: str = "yolov8n.pt",
                 classification_model: Optional[str] = None,
                 device: str = "cpu"):
        """
        Initialize enhanced detector with multiple models
        
        Args:
            detection_model: Main YOLO detection model
            classification_model: Optional secondary model for detailed classification
            device: Device to run on ('cpu' or 'cuda')
        """
        logger.info(f"[Enhanced] Initializing detector with {detection_model} on {device}")
        
        self.device = device
        self.detection_model = YOLO(detection_model)
        self.detection_model.to(device)
        
        # Load classification model if provided
        self.classification_model = None
        if classification_model:
            try:
                self.classification_model = YOLO(classification_model)
                self.classification_model.to(device)
                logger.info(f"[Enhanced] Classification model loaded: {classification_model}")
            except Exception as e:
                logger.warning(f"[Enhanced] Failed to load classification model: {e}")
    
    def predict(self, 
                image: Image.Image, 
                conf_threshold: float = 0.5,
                enable_tracking: bool = True) -> Dict[str, Any]:
        """
        Run enhanced inference with detailed classification
        
        Args:
            image: PIL Image object
            conf_threshold: Confidence threshold
            enable_tracking: Enable movement tracking features
        
        Returns:
            Dictionary with detections and analysis
        """
        start_time = time.time()
        
        try:
            # Convert to numpy array for processing
            img_array = np.array(image)
            
            # Run main detection
            results = self.detection_model(image, conf=conf_threshold, verbose=False)
            
            # Parse detections
            detections = []
            for result in results:
                boxes = result.boxes
                
                for i, box in enumerate(boxes):
                    detection = self._parse_single_detection(box, result, i)
                    
                    # Enhance with detailed classification
                    detection = self._classify_attributes(detection, img_array, box)
                    
                    detections.append(detection)
            
            # Analyze detection patterns
            analysis = self._analyze_detections(detections, img_array)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'detections': detections,
                'analysis': analysis,
                'processing_time_ms': processing_time,
                'image_metadata': {
                    'width': image.width,
                    'height': image.height,
                    'mode': image.mode
                }
            }
            
        except Exception as e:
            logger.error(f"[Enhanced] Inference error: {e}", exc_info=True)
            raise
    
    def _parse_single_detection(self, box, result, index: int) -> Dict[str, Any]:
        """Parse a single detection box"""
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        xyxy = box.xyxy[0].cpu().numpy()
        
        return {
            'id': index,
            'bbox': {
                'x': float(xyxy[0]),
                'y': float(xyxy[1]),
                'width': float(xyxy[2] - xyxy[0]),
                'height': float(xyxy[3] - xyxy[1]),
            },
            'confidence': confidence,
            'class': class_id,
            'class_name': result.names.get(class_id, 'unknown'),
            'species': self.SPECIES_MAP.get(class_id, 'Unknown'),
        }
    
    def _classify_attributes(self, 
                            detection: Dict[str, Any], 
                            image: np.ndarray,
                            box) -> Dict[str, Any]:
        """
        Enhance detection with detailed attributes
        Uses image analysis and bounding box features
        """
        bbox = detection['bbox']
        x, y, w, h = int(bbox['x']), int(bbox['y']), int(bbox['width']), int(bbox['height'])
        
        # Crop detection region
        roi = image[y:y+h, x:x+w] if y+h <= image.shape[0] and x+w <= image.shape[1] else None
        
        # Estimate gender (based on size and visual features)
        detection['gender'] = self._estimate_gender(roi, w, h)
        
        # Estimate age
        detection['age_estimate'] = self._estimate_age(roi, w, h, detection['confidence'])
        
        # Assess health status
        detection['health_status'] = self._assess_health(roi)
        
        # Estimate threat level (0-10)
        detection['threat_level'] = self._calculate_threat_level(detection)
        
        # Extract physical attributes
        detection['physical_attributes'] = self._extract_physical_attributes(roi, w, h)
        
        # Behavioral indicators
        detection['behavior_tags'] = self._infer_behavior(detection)
        
        return detection
    
    def _estimate_gender(self, roi, width: int, height: int) -> str:
        """
        Estimate gender based on size and morphological features
        Males typically larger with more robust build
        """
        if roi is None:
            return 'unknown'
        
        # Simple heuristic: larger bounding boxes may indicate males
        size_ratio = width / height if height > 0 else 1.0
        
        # Males: wider/larger, Females: smaller/slender
        if size_ratio > 1.3 and width > 150:
            return 'male'
        elif size_ratio < 1.1 and width < 120:
            return 'female'
        else:
            return 'unknown'
    
    def _estimate_age(self, roi, width: int, height: int, confidence: float) -> str:
        """Estimate age category based on size"""
        if roi is None:
            return 'unknown'
        
        # Size-based age estimation
        box_area = width * height
        
        if box_area < 5000:
            return 'juvenile'
        elif box_area < 15000:
            return 'young_adult'
        elif box_area < 30000:
            return 'adult'
        else:
            return 'elderly'
    
    def _assess_health(self, roi) -> str:
        """Assess health status based on visual indicators"""
        if roi is None:
            return 'unknown'
        
        # Analyze brightness and contrast as health indicators
        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY) if len(roi.shape) == 3 else roi
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Healthy animals typically have good contrast and mid-range brightness
            if contrast > 30 and 80 < brightness < 180:
                return 'healthy'
            elif contrast < 20:
                return 'sick'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def _calculate_threat_level(self, detection: Dict[str, Any]) -> int:
        """
        Calculate threat level (0-10) based on multiple factors
        Higher = more concerning for disease transmission
        """
        threat = 0
        
        # Species risk factors
        if detection['species'] == 'Mastomys natalensis':
            threat += 5  # Primary Lassa vector
        elif 'Mastomys' in detection['species']:
            threat += 3
        
        # Confidence modifier
        threat += int(detection['confidence'] * 2)
        
        # Health status modifier
        if detection.get('health_status') == 'sick':
            threat += 2
        
        return min(threat, 10)
    
    def _extract_physical_attributes(self, roi, width: int, height: int) -> Dict[str, Any]:
        """Extract detailed physical attributes"""
        attributes = {
            'size_category': 'unknown',
            'body_length_px': width,
            'body_height_px': height,
            'estimated_length_cm': self._pixels_to_cm(width),
            'color_profile': 'unknown'
        }
        
        # Size categorization
        if width < 100:
            attributes['size_category'] = 'small'
        elif width < 200:
            attributes['size_category'] = 'medium'
        else:
            attributes['size_category'] = 'large'
        
        # Color analysis
        if roi is not None:
            try:
                avg_color = np.mean(roi, axis=(0, 1))
                attributes['color_profile'] = {
                    'r': int(avg_color[0]),
                    'g': int(avg_color[1]),
                    'b': int(avg_color[2])
                }
            except:
                pass
        
        return attributes
    
    def _pixels_to_cm(self, pixels: int, reference_dpi: int = 96) -> float:
        """Convert pixels to centimeters (rough estimate)"""
        # Assuming standard camera distance, Mastomys ~10-15cm body length
        # This is a rough heuristic - calibrate with real data
        return (pixels / reference_dpi) * 2.54
    
    def _infer_behavior(self, detection: Dict[str, Any]) -> List[str]:
        """Infer behavioral tags from detection data"""
        behaviors = []
        
        # Confidence-based behaviors
        if detection['confidence'] > 0.9:
            behaviors.append('stationary')
        elif detection['confidence'] < 0.6:
            behaviors.append('moving_fast')
        
        # Size-based behaviors
        if detection['physical_attributes']['size_category'] == 'large':
            behaviors.append('adult_active')
        
        return behaviors
    
    def _analyze_detections(self, detections: List[Dict], image: np.ndarray) -> Dict[str, Any]:
        """Analyze all detections to determine grouping and patterns"""
        num_detections = len(detections)
        
        # Determine detection type
        if num_detections == 0:
            detection_type = 'none'
        elif num_detections == 1:
            detection_type = 'single'
        elif num_detections == 2:
            detection_type = 'pair'
        elif num_detections <= 5:
            detection_type = 'group'
        else:
            detection_type = 'colony'
        
        # Calculate clustering
        clustering_info = self._analyze_clustering(detections) if num_detections > 1 else {}
        
        # Species breakdown
        species_counts = {}
        gender_counts = {'male': 0, 'female': 0, 'unknown': 0}
        age_distribution = {age: 0 for age in self.AGE_CATEGORIES}
        
        for det in detections:
            species = det.get('species', 'Unknown')
            species_counts[species] = species_counts.get(species, 0) + 1
            
            gender = det.get('gender', 'unknown')
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            age = det.get('age_estimate', 'unknown')
            if age in age_distribution:
                age_distribution[age] += 1
        
        # Calculate colony metrics
        colony_metrics = None
        if detection_type in ['group', 'colony']:
            colony_metrics = {
                'estimated_population': num_detections,
                'density': self._calculate_density(detections, image.shape),
                'spatial_spread': self._calculate_spatial_spread(detections),
                'composition': {
                    'species': species_counts,
                    'gender': gender_counts,
                    'age': age_distribution
                }
            }
        
        return {
            'detection_type': detection_type,
            'total_count': num_detections,
            'species_breakdown': species_counts,
            'gender_distribution': gender_counts,
            'age_distribution': age_distribution,
            'clustering': clustering_info,
            'colony_metrics': colony_metrics,
            'avg_confidence': np.mean([d['confidence'] for d in detections]) if detections else 0,
            'max_threat_level': max([d.get('threat_level', 0) for d in detections], default=0)
        }
    
    def _analyze_clustering(self, detections: List[Dict]) -> Dict[str, Any]:
        """Analyze spatial clustering of detections"""
        if len(detections) < 2:
            return {}
        
        # Calculate center of mass
        centers = [(d['bbox']['x'] + d['bbox']['width']/2, 
                   d['bbox']['y'] + d['bbox']['height']/2) 
                  for d in detections]
        
        center_x = np.mean([c[0] for c in centers])
        center_y = np.mean([c[1] for c in centers])
        
        # Calculate average distance from center
        distances = [np.sqrt((c[0]-center_x)**2 + (c[1]-center_y)**2) for c in centers]
        
        return {
            'cluster_center': {'x': float(center_x), 'y': float(center_y)},
            'avg_distance_from_center': float(np.mean(distances)),
            'max_distance': float(max(distances)),
            'cluster_density': len(detections) / (max(distances) + 1)
        }
    
    def _calculate_density(self, detections: List[Dict], image_shape) -> float:
        """Calculate detection density (detections per unit area)"""
        image_area = image_shape[0] * image_shape[1]
        return len(detections) / (image_area / 1000000)  # per megapixel
    
    def _calculate_spatial_spread(self, detections: List[Dict]) -> float:
        """Calculate how spread out the detections are"""
        if len(detections) < 2:
            return 0.0
        
        centers = [(d['bbox']['x'] + d['bbox']['width']/2, 
                   d['bbox']['y'] + d['bbox']['height']/2) 
                  for d in detections]
        
        # Calculate variance in positions
        x_var = np.var([c[0] for c in centers])
        y_var = np.var([c[1] for c in centers])
        
        return float(np.sqrt(x_var + y_var))
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("[Enhanced] Cleaning up detector")
        if hasattr(self, 'detection_model'):
            del self.detection_model
        if hasattr(self, 'classification_model') and self.classification_model:
            del self.classification_model
