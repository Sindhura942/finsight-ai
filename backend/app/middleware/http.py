"""
HTTP middleware for request/response handling.

This module provides middleware for logging, error handling, and
performance monitoring of HTTP requests.

Examples:
    Middleware automatically logs all requests and handles errors
    with consistent response formats.
"""

import time
import logging
from typing import Callable
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.exceptions import FinSightException


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses.
    
    Logs all incoming requests with method, path, and duration.
    Provides structured logging for monitoring and debugging.
    """

    def __init__(self, app, logger: logging.Logger):
        """Initialize logging middleware.
        
        Args:
            app: FastAPI application
            logger: Logger instance
        """
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
            
        Returns:
            HTTP response
        """
        # Log request start
        start_time = time.time()
        request_id = self._generate_request_id()
        
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING

        self.logger.log(
            log_level,
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "method": request.method,
                "path": request.url.path,
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

    @staticmethod
    def _generate_request_id() -> str:
        """Generate unique request ID.
        
        Returns:
            Request ID based on timestamp and random values
        """
        import uuid
        return str(uuid.uuid4())


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for unified error handling.
    
    Catches exceptions and returns consistent error responses
    in JSON format.
    """

    def __init__(self, app, logger: logging.Logger):
        """Initialize error handling middleware.
        
        Args:
            app: FastAPI application
            logger: Logger instance
        """
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Catch and handle exceptions.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
            
        Returns:
            HTTP response or error response
        """
        try:
            return await call_next(request)
        except FinSightException as e:
            self.logger.warning(
                f"Application error: {e.error_code}",
                extra={
                    "error_code": e.error_code,
                    "message": e.message,
                    "path": request.url.path,
                    "details": e.details,
                },
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.error_code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            self.logger.error(
                "Unhandled exception",
                exc_info=True,
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e),
                },
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_ERROR",
                    "message": "Internal server error",
                    "timestamp": datetime.now().isoformat(),
                },
            )


class CORSMiddlewareConfig:
    """Configuration for CORS middleware.
    
    Provides centralized CORS settings.
    """

    @staticmethod
    def get_config(allowed_origins: list = None) -> dict:
        """Get CORS configuration.
        
        Args:
            allowed_origins: List of allowed origins
            
        Returns:
            CORS configuration dictionary
        """
        if allowed_origins is None:
            allowed_origins = [
                "http://localhost:3000",
                "http://localhost:8501",  # Streamlit
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8501",
            ]

        return {
            "allow_origins": allowed_origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "expose_headers": ["X-Request-ID"],
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware.
    
    Limits requests per IP address.
    """

    def __init__(self, app, logger: logging.Logger, requests_per_minute: int = 60):
        """Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            logger: Logger instance
            requests_per_minute: Max requests per minute per IP
        """
        super().__init__(app)
        self.logger = logger
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # In production, use Redis

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit and process request.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
            
        Returns:
            HTTP response or 429 if rate limited
        """
        client_ip = request.client.host if request.client else "unknown"
        
        # Simple in-memory rate limiting (use Redis in production)
        current_count = self.request_counts.get(client_ip, 0)
        
        if current_count >= self.requests_per_minute:
            self.logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={"client_ip": client_ip, "count": current_count},
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_ERROR",
                    "message": "Too many requests",
                    "retry_after": 60,
                },
            )
        
        self.request_counts[client_ip] = current_count + 1
        
        # Reset counter after 1 minute (simplified)
        # In production, use proper cache with TTL
        
        return await call_next(request)
