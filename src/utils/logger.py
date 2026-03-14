"""Logging utilities"""

import sys
from pathlib import Path

from loguru import logger


def get_logger(name: str = "FinSight AI"):
    """Get configured logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    # Remove default handler
    logger.remove()
    
    # Console output
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    
    # File output
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "finsight.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="500 MB",
        retention="7 days",
    )
    
    return logger


# Create default logger instance
logger_instance = get_logger()
