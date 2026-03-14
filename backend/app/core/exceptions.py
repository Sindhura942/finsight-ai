"""
Custom exception classes for FinSight AI.

This module defines application-specific exceptions for proper error handling
and provides a consistent error response structure.

Examples:
    Raising validation errors:
        raise ValidationError("Invalid expense amount")
    
    Raising business logic errors:
        raise BusinessLogicError("Budget limit exceeded")
"""

from typing import Any, Dict, Optional


class FinSightException(Exception):
    """Base exception class for all FinSight AI exceptions.
    
    Attributes:
        message: Error message
        error_code: Application-specific error code
        status_code: HTTP status code
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize FinSightException.
        
        Args:
            message: Human-readable error message
            error_code: Application error code for logging
            status_code: HTTP status code
            details: Additional error context
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses.
        
        Returns:
            Dictionary with error information
        """
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(FinSightException):
    """Raised when input validation fails.
    
    Used for invalid data formats, missing required fields, or constraint violations.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize ValidationError with 400 status code."""
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(FinSightException):
    """Raised when requested resource is not found.
    
    Used when expense, budget, or other resource doesn't exist.
    """

    def __init__(self, message: str, resource_type: str = "Resource"):
        """Initialize NotFoundError with 404 status code."""
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type},
        )


class BusinessLogicError(FinSightException):
    """Raised when business logic constraints are violated.
    
    Used for budget exceeded, invalid state transitions, or business rule violations.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize BusinessLogicError with 400 status code."""
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=400,
            details=details,
        )


class DatabaseError(FinSightException):
    """Raised when database operations fail.
    
    Used for connection errors, constraint violations, or query failures.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize DatabaseError with 500 status code."""
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )


class ExternalServiceError(FinSightException):
    """Raised when external service calls fail.
    
    Used for OCR service failures, AI service errors, or API timeouts.
    """

    def __init__(self, service: str, message: str, retryable: bool = True):
        """Initialize ExternalServiceError with 503 status code.
        
        Args:
            service: Name of the external service
            message: Error message
            retryable: Whether the error is retryable
        """
        super().__init__(
            message=f"{service} service error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=503,
            details={"service": service, "retryable": retryable},
        )


class AuthenticationError(FinSightException):
    """Raised when authentication fails.
    
    Used for invalid credentials or missing authentication.
    """

    def __init__(self, message: str = "Authentication failed"):
        """Initialize AuthenticationError with 401 status code."""
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
        )


class AuthorizationError(FinSightException):
    """Raised when user lacks required permissions.
    
    Used for access control violations.
    """

    def __init__(self, message: str = "Insufficient permissions"):
        """Initialize AuthorizationError with 403 status code."""
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
        )


class RateLimitError(FinSightException):
    """Raised when rate limit is exceeded.
    
    Used for API rate limiting.
    """

    def __init__(self, retry_after: int = 60):
        """Initialize RateLimitError with 429 status code.
        
        Args:
            retry_after: Seconds to retry after
        """
        super().__init__(
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_ERROR",
            status_code=429,
            details={"retry_after": retry_after},
        )
