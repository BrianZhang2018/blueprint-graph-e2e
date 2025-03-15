"""
Logging configuration for the application.
"""
import sys
import logging
from loguru import logger
from .config import settings


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages toward Loguru.
    
    This handler intercepts all standard logging messages and redirects them
    to Loguru for consistent formatting and handling.
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Configure logging for the application.
    
    This function sets up Loguru as the main logging provider and
    intercepts all standard library logging.
    """
    # Remove default loguru handler
    logger.remove()
    
    # Add custom handler with desired format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Add stdout handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
    )
    
    # Add file handler for non-development environments
    if settings.environment != "development":
        logger.add(
            "logs/blueprintgraph.log",
            rotation="10 MB",
            retention="1 week",
            format=log_format,
            level=settings.log_level,
            compression="zip",
        )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Update logging levels for some noisy libraries
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
    
    return logger


# Create a global logger instance
log = setup_logging() 