#!/usr/bin/env python3
"""
Automated Capture Loop - No Manual Intervention
Continuously captures frames from RTSP streams and sends to inference
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capture_service.app import SkyhawkCaptureService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("capture_service.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for automated capture"""
    logger.info("=" * 60)
    logger.info("🚀 SKYHAWK AUTONOMOUS DETECTION SYSTEM")
    logger.info("=" * 60)
    logger.info("Mode: FULLY AUTOMATED - No manual intervention")
    logger.info("Flow: RTSP → Frame Capture → YOLO Inference → Database → Map")
    logger.info("=" * 60)
    
    # Environment check
    required_vars = ["DATABASE_URL"]
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        logger.warning(f"⚠️  Missing environment variables: {', '.join(missing)}")
        logger.warning("⚠️  Detections will not persist to database")
        logger.warning("Set them in .env or export them before running")
    
    # Start service
    try:
        service = SkyhawkCaptureService()
        logger.info("✅ Service initialized")
        logger.info("🎥 Starting RTSP watchers...")
        logger.info("🧠 ML inference will run automatically")
        logger.info("🌍 Detections will appear on Cesium map in real-time")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        service.start()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("👋 Capture service stopped")

if __name__ == "__main__":
    main()
