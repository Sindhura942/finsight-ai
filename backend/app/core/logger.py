"""Application logger configuration"""

import sys

from loguru import logger

from .config import settings


def configure_logger():
    """Configure loguru logger"""

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
    )

    # Add file handler
    logger.add(
        "logs/finsight.log",
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="500 MB",
        retention="7 days",
    )

    return logger


app_logger = configure_logger()
