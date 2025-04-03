import logging
import importlib
import sys
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
        # For specific module, try both formats for compatibility
        module_path = f"{package_name}.{module}"  # Path for __name__

        # Get and configure the logger
        logger = logging.getLogger(module_path)
        logger.setLevel(level)
        if not logger.handlers:
            _add_handler(logger)
        _loggers[module_path] = logger
        return _loggers

    # For all modules in the package
    import alpha.datasets
    import inspect
    import importlib

    # Find all modules in the package
    modules = ["loader", "storage"]  # Core modules we know about

    for module_name in modules:
        # Import the module to ensure it's loaded
        module_path = f"{package_name}.{module_name}"
        logger = logging.getLogger(module_path)
        logger.setLevel(level)
        if not logger.handlers:
            _add_handler(logger)
        _loggers[module_path] = logger

    return _loggers


def _add_handler(logger):
    """Add a standard handler to a logger"""
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


__all__ = ["load_daily", "AssetType", "list_available_months", "set_log_level"]
