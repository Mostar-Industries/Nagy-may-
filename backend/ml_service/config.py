"""
ML Service configuration module.
Extends shared_config with YOLO-specific settings and fallback logic.
"""

from backend.shared_config import Config
import os
import logging

logger = logging.getLogger(__name__)


class MLConfig(Config):
    """ML-specific configuration"""

    @staticmethod
    def ml_port() -> int:
        """Get ML service port"""
        return int(os.getenv("ML_PORT", "5001"))

    @staticmethod
    def model_cache_dir() -> str:
        """Get model cache directory"""
        return os.getenv("MODEL_CACHE_DIR", "./models")

    @staticmethod
    def enable_gpu() -> bool:
        """Check if GPU is available and enabled"""
        device = Config.device()
        return device.lower() in ["cuda", "gpu"]

    @staticmethod
    def initialize():
        """Initialize ML config and print summary"""
        logger.info("Initializing ML Service Configuration...")
        logger.info(f"Port: {MLConfig.ml_port()}")
        logger.info(f"Model Cache: {MLConfig.model_cache_dir()}")
        logger.info(f"GPU Enabled: {MLConfig.enable_gpu()}")
        Config.print_config_summary()
