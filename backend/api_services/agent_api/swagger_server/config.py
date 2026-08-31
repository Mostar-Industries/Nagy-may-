"""
Agent Service configuration module.
Extends shared_config with Agent-specific settings and fallback logic.
"""

from backend.shared_config import Config
import os
import logging

logger = logging.getLogger(__name__)


class AgentConfig(Config):
    """Agent-specific configuration"""

    @staticmethod
    def agent_title() -> str:
        """Get Agent title"""
        return "MNTRK AI Agent by MoStar Industries"

    @staticmethod
    def agent_version() -> str:
        """Get Agent version"""
        return "1.0.0"

    @staticmethod
    def max_conversation_turns() -> int:
        """Get maximum conversation turns"""
        return int(os.getenv("MAX_CONVERSATION_TURNS", "10"))

    @staticmethod
    def response_timeout_seconds() -> int:
        """Get response timeout in seconds"""
        return int(os.getenv("RESPONSE_TIMEOUT_SECONDS", "30"))

    @staticmethod
    def initialize():
        """Initialize Agent config and print summary"""
        logger.info("Initializing Agent Service Configuration...")
        logger.info(f"Title: {AgentConfig.agent_title()}")
        logger.info(f"Version: {AgentConfig.agent_version()}")
        logger.info(f"Max Conversation Turns: {AgentConfig.max_conversation_turns()}")
        logger.info(f"Response Timeout: {AgentConfig.response_timeout_seconds()}s")
        Config.print_config_summary()
