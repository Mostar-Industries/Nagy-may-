"""
Shared configuration and environment management for all Skyhawk services.
Provides fallback logic to open public datasets when API keys are missing.
"""

import os
from typing import Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Mode(Enum):
    """App mode: SECURE (with API keys) or OPEN (using public data)"""
    SECURE = "secure"
    OPEN = "open"


class Config:
    """
    Centralized configuration with automatic fallback logic.
    Missing API keys gracefully degrade to open-source alternatives.
    """

    # Determine app mode based on available API keys
    @staticmethod
    def get_mode() -> Mode:
        """Determine if we're in SECURE or OPEN mode"""
        has_api_keys = bool(
            os.getenv("GEMINI_API_KEY") or
            os.getenv("OPENWEATHER_API_KEY") or
            os.getenv("SORMAS_API_KEY")
        )
        return Mode.SECURE if has_api_keys else Mode.OPEN

    # DATABASE CONFIGURATION
    @staticmethod
    def database_url() -> str:
        """Get database URL from environment or raise error"""
        url = os.getenv("DATABASE_URL")
        if not url:
            raise ValueError("DATABASE_URL environment variable is required")
        return url

    @staticmethod
    def postgres_port() -> int:
        """Get PostgreSQL port"""
        return int(os.getenv("POSTGRES_PORT", "5432"))

    # API SERVER CONFIGURATION
    @staticmethod
    def api_port() -> int:
        """Get API server port"""
        return int(os.getenv("API_PORT", "5002"))

    @staticmethod
    def api_host() -> str:
        """Get API server host"""
        return os.getenv("API_HOST", "0.0.0.0")

    @staticmethod
    def agent_port() -> int:
        """Get Agent server port"""
        return int(os.getenv("AGENT_PORT", "5003"))

    @staticmethod
    def ml_service_url() -> str:
        """Get ML service URL for inference calls"""
        return os.getenv("ML_SERVICE_URL", "http://localhost:5001")

    # YOLO CONFIGURATION
    @staticmethod
    def yolo_model() -> str:
        """Get YOLO model name"""
        return os.getenv("YOLO_MODEL", "yolov8n.pt")

    @staticmethod
    def yolo_confidence_threshold() -> float:
        """Get YOLO confidence threshold"""
        return float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.5"))

    @staticmethod
    def yolo_iou_threshold() -> float:
        """Get YOLO IOU threshold"""
        return float(os.getenv("YOLO_IOU_THRESHOLD", "0.4"))

    @staticmethod
    def device() -> str:
        """Get device for YOLO inference (cpu or cuda)"""
        return os.getenv("DEVICE", "cpu")

    @staticmethod
    def max_upload_size_mb() -> int:
        """Get maximum upload size in MB"""
        return int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    # AI & LLM CONFIGURATION
    @staticmethod
    def gemini_api_key() -> Optional[str]:
        """Get Gemini API key (optional)"""
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            logger.warning(
                "GEMINI_API_KEY not set. Agent will use fallback prompts only."
            )
        return key

    @staticmethod
    def use_gemini() -> bool:
        """Check if Gemini integration is enabled"""
        return bool(Config.gemini_api_key())

    @staticmethod
    def context_length() -> int:
        """Get context length for agent responses"""
        return int(os.getenv("CONTEXT_LENGTH", "2048"))

    # EXTERNAL API CONFIGURATION WITH FALLBACKS
    @staticmethod
    def weather_api_config() -> Dict[str, Any]:
        """
        Weather API configuration with fallback to Open-Meteo
        """
        key = os.getenv("OPENWEATHER_API_KEY")
        if key:
            logger.info("Using OpenWeather API")
            return {
                "provider": "openweather",
                "api_key": key,
                "base_url": "https://api.openweathermap.org/data/2.5"
            }
        else:
            logger.info("Using Open-Meteo (fallback) for weather data")
            return {
                "provider": "open-meteo",
                "api_key": None,
                "base_url": "https://api.open-meteo.com/v1"
            }

    @staticmethod
    def sormas_api_config() -> Dict[str, Any]:
        """
        SORMAS API configuration with fallback to mock data
        """
        key = os.getenv("SORMAS_API_KEY")
        url = os.getenv("SORMAS_API_URL")
        if key and url:
            logger.info("Using SORMAS API")
            return {
                "enabled": True,
                "api_key": key,
                "base_url": url
            }
        else:
            logger.info("Using mock SORMAS data (fallback)")
            return {
                "enabled": False,
                "api_key": None,
                "base_url": None,
                "fallback_data_file": "data/mock/sormas_outbreaks.json"
            }

    @staticmethod
    def cdc_api_config() -> Dict[str, Any]:
        """
        CDC API configuration with fallback to CSV data
        """
        key = os.getenv("CDC_API_KEY")
        if key:
            logger.info("Using CDC API")
            return {
                "enabled": True,
                "api_key": key,
                "base_url": "https://cdc.gov/api"
            }
        else:
            logger.info("Using CDC epidemiology CSV (fallback)")
            return {
                "enabled": False,
                "api_key": None,
                "fallback_data_file": "data/mock/cdc_trends.csv"
            }

    @staticmethod
    def nphcda_api_config() -> Dict[str, Any]:
        """
        NPHCDA (Nigeria) API configuration with fallback to local CSV
        """
        key = os.getenv("NPHCDA_API_KEY")
        if key:
            logger.info("Using NPHCDA API")
            return {
                "enabled": True,
                "api_key": key,
                "base_url": "https://nphcda.gov.ng/api"
            }
        else:
            logger.info("Using Nigeria health data CSV (fallback)")
            return {
                "enabled": False,
                "api_key": None,
                "fallback_data_file": "data/mock/nigeria_health.csv"
            }

    @staticmethod
    def external_apis() -> Dict[str, Dict[str, Any]]:
        """Get all external API configurations"""
        return {
            "weather": Config.weather_api_config(),
            "sormas": Config.sormas_api_config(),
            "cdc": Config.cdc_api_config(),
            "nphcda": Config.nphcda_api_config(),
        }

    # FEATURE FLAGS
    @staticmethod
    def enable_websocket() -> bool:
        """Enable WebSocket support for real-time updates"""
        return os.getenv("ENABLE_WEBSOCKET", "true").lower() == "true"

    @staticmethod
    def enable_batch_processing() -> bool:
        """Enable batch image processing"""
        return os.getenv("ENABLE_BATCH_PROCESSING", "false").lower() == "true"

    @staticmethod
    def enable_cache() -> bool:
        """Enable caching for inference results"""
        return os.getenv("ENABLE_CACHE", "true").lower() == "true"

    # LOGGING
    @staticmethod
    def log_level() -> str:
        """Get logging level"""
        return os.getenv("LOG_LEVEL", "info").upper()

    @staticmethod
    def flask_env() -> str:
        """Get Flask environment"""
        return os.getenv("FLASK_ENV", "development")

    # UTILITY METHODS
    @staticmethod
    def print_config_summary():
        """Print current configuration for debugging"""
        logger.info("=" * 60)
        logger.info("SKYHAWK SYSTEM CONFIGURATION")
        logger.info("=" * 60)
        logger.info(f"Mode: {Config.get_mode().value.upper()}")
        logger.info(f"Flask Env: {Config.flask_env()}")
        logger.info(f"Log Level: {Config.log_level()}")
        logger.info(f"API Port: {Config.api_port()}")
        logger.info(f"Agent Port: {Config.agent_port()}")
        logger.info(f"ML Service: {Config.ml_service_url()}")
        logger.info(f"YOLO Model: {Config.yolo_model()}")
        logger.info(f"Device: {Config.device()}")
        logger.info(f"Gemini Enabled: {Config.use_gemini()}")
        logger.info(f"WebSocket Enabled: {Config.enable_websocket()}")
        logger.info(f"Batch Processing Enabled: {Config.enable_batch_processing()}")
        logger.info("External APIs:")
        for api_name, config in Config.external_apis().items():
            status = "✓ Enabled" if config.get("enabled", False) else "✗ Fallback"
            logger.info(f"  {api_name}: {status}")
        logger.info("=" * 60)
