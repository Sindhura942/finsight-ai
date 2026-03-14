"""Validation utilities"""

from pathlib import Path
from typing import Tuple

from src.config import get_settings


def validate_image_file(filename: str) -> bool:
    """Validate image file extension
    
    Args:
        filename: Name of the file
        
    Returns:
        True if valid image file
    """
    settings = get_settings()
    file_ext = "." + filename.rsplit(".", 1)[-1].lower()
    return file_ext in settings.allowed_extensions


def validate_file_size(file_size_bytes: int) -> Tuple[bool, str]:
    """Validate file size
    
    Args:
        file_size_bytes: File size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    
    if file_size_bytes > max_bytes:
        return False, f"File exceeds {settings.max_upload_size_mb}MB limit"
    
    return True, ""


def validate_image_path(path: str) -> bool:
    """Validate image file exists
    
    Args:
        path: Path to image file
        
    Returns:
        True if file exists
    """
    return Path(path).exists() and Path(path).is_file()
