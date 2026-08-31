"""
API Service configuration module.
Extends shared_config with API-specific settings and fallback logic.
"""

from backend.shared_config import Config
import os
import logging

logger = logging.getLogger(__name__)


class APIConfig(Config):
    """API-specific configuration"""

    @staticmethod
    def cors_origins() -> list:
        """Get CORS allowed origins"""
        origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
        return [origin.strip() for origin in origins.split(",")]

    @staticmethod
    def api_title() -> str:
        """Get API title"""
        return "MNTRK Detection API by MoStar Industries"

    @staticmethod
    def api_version() -> str:
        """Get API version"""
        return "1.0.0"

    @staticmethod
    def initialize():
        """Initialize API config and print summary"""
        logger.info("Initializing API Service Configuration...")
        logger.info(f"Title: {APIConfig.api_title()}")
        logger.info(f"Version: {APIConfig.api_version()}")
        logger.info(f"CORS Origins: {APIConfig.cors_origins()}")
        Config.print_config_summary()
