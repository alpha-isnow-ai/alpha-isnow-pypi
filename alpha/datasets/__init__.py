import logging
import importlib
import pkgutil
from .loader import load_daily, list_available_months
from .enums import AssetType

_loggers = {}

# Configure root logger to prevent propagation issues
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s - %(message)s",
    level=logging.ERROR,  # Default level
)


def set_log_level(level, module=None):
    """Set log level for package modules"""
    package_name = "alpha.datasets"

    if module:
        # Set log level for a specific module
        logger_name = f"{package_name}.{module}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        if not logger.handlers:
            _add_handler(logger)
        _loggers[logger_name] = logger
        return _loggers

    # Manually set known loggers to avoid import side effects
    for module_name in ["loader", "storage"]:
        logger_name = f"{package_name}.{module_name}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        if not logger.handlers:
            _add_handler(logger)
        _loggers[logger_name] = logger

    return _loggers


def _add_handler(logger):
    """Add a standard handler to a logger"""
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


__all__ = ["load_daily", "AssetType", "list_available_months", "set_log_level"]
