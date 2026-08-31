"""
Enhanced Capture Service Integration
Dual robust system: Capture Service + ML Service coordination
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, List
import json
import httpx
from PIL import Image
import cv2
import numpy as np
import io
from ultralytics import YOLO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DualDetectionOrchestrator:
    """
    Orchestrates detection between Capture Service (local) and ML Service (centralized)
    Authority: Detection routing, failover management, result synthesis
    """
    
    def __init__(self):
        self.ml_service_url = os.getenv('YOLO_API_URL', 'http://ml-service:5001')
        # Point to a local model file for edge inference
        self.local_model_path = os.getenv('YOLO_MODEL_PATH', '/app/models/weights/yolo11n.pt')
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.local_model = None
        self.local_model_loaded = False
        
    async def initialize_local_model(self):
        """Initialize local YOLO model for capture service"""
        try:
            if os.path.exists(self.local_model_path):
                self.local_model = YOLO(self.local_model_path)
                self.local_model_loaded = True
                logger.info(f"Local YOLO11n model loaded in capture service from {self.local_model_path}")
            else:
                logger.warning(f"Local model not found at {self.local_model_path}, looking for backup...")
                # Search common locations or use a default if it exists
                if os.path.exists('yolov8n.pt'):
                    self.local_model = YOLO('yolov8n.pt')
                    self.local_model_loaded = True
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
    
    async def detect_with_dual_system(self, image_data: bytes, source_info: Dict) -> Dict:
        """
        Dual detection system with failover
        Priority: ML Service → Local Capture → Mock (for testing)
        """
        detection_results = {
            'detection_strategy': None,
            'primary_result': None,
            'backup_result': None,
            'synthesis': None
        }
        
        # Strategy 1: Try ML Service first (centralized processing)
        ml_result = await self._try_ml_service_detection(image_data, source_info)
        
        if ml_result and ml_result.get('status') == 'success':
            detection_results['detection_strategy'] = 'ml_service_primary'
            detection_results['primary_result'] = ml_result
            
            # Optional: Run local detection for comparison/validation
            local_result = await self._try_local_detection(image_data, source_info)
            if local_result:
                detection_results['backup_result'] = local_result
                detection_results['synthesis'] = self._synthesize_dual_results(ml_result, local_result)
                
            return detection_results
        
        # Strategy 2: Fallback to local capture detection
        logger.warning("ML Service unavailable, using local capture detection")
        local_result = await self._try_local_detection(image_data, source_info)
        
        if local_result:
            detection_results['detection_strategy'] = 'local_capture_fallback'
            detection_results['primary_result'] = local_result
            return detection_results
        
        # Strategy 3: Emergency mock for testing
        logger.error("Both ML Service and local detection failed, using emergency mock")
        mock_result = self._generate_emergency_mock(source_info)
        detection_results['detection_strategy'] = 'emergency_mock'
        detection_results['primary_result'] = mock_result
        
        return detection_results
    
    async def _try_ml_service_detection(self, image_data: bytes, source_info: Dict) -> Optional[Dict]:
        """Try detection via centralized ML Service"""
        try:
            # Prepare multipart form data
            files = {'file': ('detection.jpg', image_data, 'image/jpeg')}
            data = {
                'latitude': source_info.get('latitude'),
                'longitude': source_info.get('longitude'),
                'source_id': source_info.get('source_id', 'capture_service'),
                'enhance_with_remostar': True
            }
            
            response = await self.http_client.post(
                f"{self.ml_service_url}/detect",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                result['detection_source'] = 'ml_service'
                return result
            else:
                logger.error(f"ML Service returned {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"ML Service detection failed: {e}")
            return None
    
    async def _try_local_detection(self, image_data: bytes, source_info: Dict) -> Optional[Dict]:
        """Try detection using local YOLO model"""
        if not self.local_model_loaded:
            return None
        
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_data))
            if image.mode in ['RGBA', 'LA']:
                image = image.convert('RGB')
            
            img_array = np.array(image)
            
            # Run local YOLO inference
            results = self.local_model(
                img_array,
                conf=0.5,
                iou=0.4,
                device='cpu',  # Capture service typically runs on CPU
                verbose=False
            )
            
            # Process results (simplified version)
            detections = []
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                
                for i, box in enumerate(boxes):
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    bbox = box.xyxy[0].tolist()
                    
                    # Simple species mapping
                    species = 'Mastomys_natalensis' if class_id == 0 else 'Other_rodent'
                    
                    detection = {
                        'detection_id': f"local_det_{i}",
                        'species': species,
                        'confidence': round(confidence, 4),
                        'bbox': {
                            'x1': round(bbox[0], 2),
                            'y1': round(bbox[1], 2),
                            'x2': round(bbox[2], 2),
                            'y2': round(bbox[3], 2)
                        },
                        'class_id': class_id,
                        'risk_priority': 'high' if species == 'Mastomys_natalensis' and confidence > 0.8 else 'medium'
                    }
                    detections.append(detection)
            
            return {
                'status': 'success',
                'detection_source': 'local_capture',
                'timestamp': datetime.utcnow().isoformat(),
                'model_info': {
                    'model_type': 'local_yolo11n',
                    'device': 'cpu'
                },
                'detections': detections,
                'detection_summary': {
                    'total_detections': len(detections),
                    'species_detected': list(set([d['species'] for d in detections])),
                    'max_confidence': max([d['confidence'] for d in detections]) if detections else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Local detection failed: {e}")
            return None
    
    def _generate_emergency_mock(self, source_info: Dict) -> Dict:
        """Generate emergency mock detection for testing"""
        return {
            'status': 'emergency_mock',
            'detection_source': 'emergency_fallback',
            'timestamp': datetime.utcnow().isoformat(),
            'model_info': {
                'model_type': 'emergency_mock',
                'note': 'Both ML Service and local detection unavailable'
            },
            'detections': [
                {
                    'detection_id': 'mock_emergency',
                    'species': 'Mastomys_natalensis',
                    'confidence': 0.75,
                    'bbox': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200},
                    'class_id': 0,
                    'risk_priority': 'high'
                }
            ],
            'detection_summary': {
                'total_detections': 1,
                'species_detected': ['Mastomys_natalensis'],
                'max_confidence': 0.75
            },
            'emergency_notice': 'This is emergency mock data - verify detection systems'
        }
    
    def _synthesize_dual_results(self, ml_result: Dict, local_result: Dict) -> Dict:
        """Synthesize results from both detection systems"""
        ml_detections = ml_result.get('detections', [])
        local_detections = local_result.get('detections', [])
        
        return {
            'dual_detection_analysis': {
                'ml_service_count': len(ml_detections),
                'local_capture_count': len(local_detections),
                'detection_agreement': self._assess_detection_agreement(ml_detections, local_detections),
                'confidence_comparison': self._compare_confidence_scores(ml_detections, local_detections),
                'recommended_result': 'ml_service' if len(ml_detections) >= len(local_detections) else 'local_capture'
            },
            'quality_metrics': {
                'dual_system_reliability': 'high',
                'result_consistency': self._assess_consistency(ml_detections, local_detections),
                'system_redundancy': 'active'
            }
        }
    
    def _assess_detection_agreement(self, ml_detections: list, local_detections: list) -> str:
        """Assess agreement between detection systems"""
        if not ml_detections and not local_detections:
            return 'both_no_detection'
        elif len(ml_detections) > 0 and len(local_detections) > 0:
            return 'both_detected'
        else:
            return 'partial_agreement'
    
    def _compare_confidence_scores(self, ml_detections: list, local_detections: list) -> Dict:
        """Compare confidence scores between systems"""
        ml_avg = sum([d.get('confidence', 0) for d in ml_detections]) / len(ml_detections) if ml_detections else 0
        local_avg = sum([d.get('confidence', 0) for d in local_detections]) / len(local_detections) if local_detections else 0
        
        return {
            'ml_service_avg_confidence': round(ml_avg, 3),
            'local_capture_avg_confidence': round(local_avg, 3),
            'confidence_differential': round(abs(ml_avg - local_avg), 3)
        }
    
    def _assess_consistency(self, ml_detections: list, local_detections: list) -> str:
        """Assess consistency between detection systems"""
        if not ml_detections or not local_detections:
            return 'insufficient_data'
        
        # Simple consistency check based on species detection
        ml_species = set([d.get('species', '') for d in ml_detections])
        local_species = set([d.get('species', '') for d in local_detections])
        
        overlap = len(ml_species.intersection(local_species))
        total_unique = len(ml_species.union(local_species))
        
        if total_unique == 0:
            return 'no_detections'
        
        consistency_ratio = overlap / total_unique
        
        if consistency_ratio > 0.8:
            return 'high_consistency'
        elif consistency_ratio > 0.5:
            return 'moderate_consistency'
        else:
            return 'low_consistency'


# Integration function for capture service
async def process_frame_with_dual_detection(frame: np.ndarray, source_info: Dict) -> Dict:
    """
    Process video frame with dual detection system
    For use in capture service main loop
    """
    orchestrator = DualDetectionOrchestrator()
    await orchestrator.initialize_local_model()
    
    # Convert frame to image bytes
    _, encoded = cv2.imencode('.jpg', frame)
    image_bytes = encoded.tobytes()
    
    # Run dual detection
    detection_results = await orchestrator.detect_with_dual_system(image_bytes, source_info)
    
    return detection_results

# Mock testing utilities
class MockDetectionGenerator:
    """Generate realistic mock detection data for testing consciousness layers"""
    
    @staticmethod
    def generate_mastomys_detection(confidence: float = 0.85, count: int = 1) -> Dict:
        """Generate mock M. natalensis detection"""
        detections = []
        
        for i in range(count):
            detection = {
                'detection_id': f"mock_natalensis_{i}",
                'species': 'Mastomys_natalensis',
                'confidence': round(confidence - (i * 0.02), 4),
                'bbox': {
                    'x1': 50 + (i * 30),
                    'y1': 75 + (i * 25),
                    'x2': 150 + (i * 30),
                    'y2': 175 + (i * 25)
                },
                'class_id': 0,
                'risk_priority': 'critical' if confidence > 0.9 else 'high'
            }
            detections.append(detection)
        
        return {
            'status': 'mock_success',
            'detection_source': 'mock_generator',
            'timestamp': datetime.utcnow().isoformat(),
            'model_info': {
                'model_type': 'mock_yolo11n_consciousness_testing',
                'purpose': 'consciousness_layer_testing'
            },
            'detections': detections,
            'detection_summary': {
                'total_detections': len(detections),
                'species_detected': ['Mastomys_natalensis'],
                'max_confidence': confidence,
                'high_risk_detections': len(detections)
            }
        }
    
    @staticmethod
    def generate_multi_species_detection() -> Dict:
        """Generate mock multi-species detection for complex consciousness testing"""
        detections = [
            {
                'detection_id': 'mock_multi_1',
                'species': 'Mastomys_natalensis',
                'confidence': 0.92,
                'bbox': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200},
                'class_id': 0,
                'risk_priority': 'critical'
            },
            {
                'detection_id': 'mock_multi_2',
                'species': 'Mastomys_erythroleucus',
                'confidence': 0.78,
                'bbox': {'x1': 250, 'y1': 150, 'x2': 350, 'y2': 250},
                'class_id': 1,
                'risk_priority': 'high'
            },
            {
                'detection_id': 'mock_multi_3',
                'species': 'Rattus_rattus',
                'confidence': 0.65,
                'bbox': {'x1': 50, 'y1': 300, 'x2': 120, 'y2': 370},
                'class_id': 4,
                'risk_priority': 'medium'
            }
        ]
        
        return {
            'status': 'mock_success',
            'detection_source': 'mock_multi_species',
            'timestamp': datetime.utcnow().isoformat(),
            'model_info': {
                'model_type': 'mock_multi_species_testing',
                'purpose': 'complex_consciousness_analysis'
            },
            'detections': detections,
            'detection_summary': {
                'total_detections': 3,
                'species_detected': ['Mastomys_natalensis', 'Mastomys_erythroleucus', 'Rattus_rattus'],
                'max_confidence': 0.92,
                'high_risk_detections': 2
            }
        }
