"""Helper utilities"""

from datetime import datetime
from typing import Optional


def format_currency(amount: float, currency: str = "$") -> str:
    """Format amount as currency string
    
    Args:
        amount: Amount to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    return f"{currency}{amount:.2f}"


def parse_date(date_string: str, format: str = "%Y-%m-%d") -> Optional[datetime]:
    """Parse date string to datetime
    
    Args:
        date_string: Date string to parse
        format: Expected date format
        
    Returns:
        Parsed datetime or None if invalid
    """
    try:
        return datetime.strptime(date_string, format)
    except ValueError:
        return None


def extract_numbers(text: str) -> list:
    """Extract numbers from text
    
    Args:
        text: Text to extract numbers from
        
    Returns:
        List of numbers found
    """
    import re
    return re.findall(r'\d+\.?\d*', text)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
