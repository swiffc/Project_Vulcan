"""
Logging Configuration Module

Provides centralized logging configuration for Project Vulcan.
Loads configuration from YAML file with rotation and multiple handlers.
"""

import logging
import logging.config
import yaml
from pathlib import Path
from typing import Optional

# Default logging format if YAML config fails
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LEVEL = logging.INFO


def setup_logging(
    config_path: Optional[Path] = None, log_level: Optional[str] = None
) -> None:
    """
    Set up logging configuration from YAML file.

    Args:
        config_path: Path to logging.yaml config file (default: config/logging.yaml)
        log_level: Override log level from environment (DEBUG, INFO, WARNING, ERROR)

    Example:
        >>> from core.logging_config import setup_logging
        >>> setup_logging()
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    # Determine config path
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "logging.yaml"

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    try:
        # Load YAML configuration
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Override log level if specified
            if log_level:
                level = getattr(logging, log_level.upper(), DEFAULT_LEVEL)
                config["root"]["level"] = level

                # Update all loggers
                for logger_config in config.get("loggers", {}).values():
                    logger_config["level"] = level

            # Apply configuration
            logging.config.dictConfig(config)

            logger = logging.getLogger(__name__)
            logger.info(f"Logging configured from {config_path}")
            logger.info(f"Log files: logs/vulcan.log, logs/error.log")

        else:
            # Fallback to basic configuration
            _setup_basic_logging(log_level)
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Logging config not found at {config_path}, using basic config"
            )

    except Exception as e:
        # Fallback to basic configuration on error
        _setup_basic_logging(log_level)
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to load logging config: {e}", exc_info=True)
        logger.info("Using basic logging configuration")


def _setup_basic_logging(log_level: Optional[str] = None) -> None:
    """Set up basic logging configuration as fallback."""
    level = DEFAULT_LEVEL
    if log_level:
        level = getattr(logging, log_level.upper(), DEFAULT_LEVEL)

    logging.basicConfig(
        level=level,
        format=DEFAULT_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/vulcan.log", encoding="utf-8"),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> from core.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request")
    """
    return logging.getLogger(name)


# Convenience function for testing
if __name__ == "__main__":
    import os

    # Test logging configuration
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level=log_level)

    logger = get_logger(__name__)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    print("\nLog files created:")
    print("  - logs/vulcan.log (all logs)")
    print("  - logs/error.log (errors only)")
