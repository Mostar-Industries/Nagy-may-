#!/usr/bin/env python3
"""
YOLO Inference API for Mastomys Detection
Command-line interface for running inference on images
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from PIL import Image
from models.yolo_detector import YOLODetector
from models.enhanced_detector import EnhancedMastomysDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Run YOLO inference on an image')
    parser.add_argument('--image', type=str, required=True, help='Path to image file')
    parser.add_argument('--conf', type=float, default=0.5, help='Confidence threshold')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Model file')
    parser.add_argument('--device', type=str, default='cpu', choices=['cpu', 'cuda'], help='Device to use')
    parser.add_argument('--output', type=str, default='json', choices=['json', 'text'], help='Output format')
    parser.add_argument('--enhanced', action='store_true', help='Use enhanced detector with detailed classification')
    
    args = parser.parse_args()
    
    try:
        # Load image
        image_path = Path(args.image)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {args.image}")
        
        image = Image.open(image_path)
        logger.info(f"Loaded image: {image_path} ({image.size})")
        
        # Initialize detector
        if args.enhanced:
            logger.info("Using enhanced detector with detailed classification")
            detector = EnhancedMastomysDetector(
                detection_model=args.model,
                device=args.device
            )
            result = detector.predict(image, conf_threshold=args.conf)
            detections = result['detections']
            analysis = result.get('analysis', {})
        else:
            detector = YOLODetector(model_name=args.model, device=args.device)
            detections = detector.predict(image, conf_threshold=args.conf)
            analysis = {}
        
        # Output results
        if args.output == 'json':
            result = {
                'success': True,
                'image_path': str(image_path),
                'detections': detections,
                'count': len(detections),
                'analysis': analysis if args.enhanced else None
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Found {len(detections)} detections:")
            if args.enhanced and analysis:
                print(f"Detection Type: {analysis.get('detection_type', 'N/A')}")
                print(f"Total Count: {analysis.get('total_count', 0)}")
                print()
            
            for i, det in enumerate(detections):
                print(f"{i+1}. {det['species']} - Confidence: {det['confidence']:.2f}")
                print(f"   Gender: {det.get('gender', 'N/A')}")
                print(f"   Age: {det.get('age_estimate', 'N/A')}")
                print(f"   Health: {det.get('health_status', 'N/A')}")
                print(f"   Threat Level: {det.get('threat_level', 0)}")
                print(f"   BBox: {det['bbox']}")
                print()
        
        # Cleanup
        detector.cleanup()
        
        return 0
        
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        if args.output == 'json':
            error_result = {
                'success': False,
                'error': str(e),
                'detections': []
            }
            print(json.dumps(error_result))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
