"""
Base service class for FinSight AI business logic.

This module provides a base service class that handles common operations
like logging, error handling, and dependency injection.

Examples:
    Creating a service:
        class ExpenseService(BaseService):
            def create_expense(self, expense_data):
                self.logger.info("Creating expense", extra={"data": expense_data})
                return self._call_repository(self.repo.create, expense_data)
"""

import logging
from typing import Any, Callable, Optional, TypeVar, Generic

from app.core.exceptions import DatabaseError, FinSightException

T = TypeVar("T")


class BaseService(Generic[T]):
    """Base service class for business logic layers.
    
    Provides common functionality like logging, error handling, and
    standardized repository access patterns.
    
    Attributes:
        logger: Configured logger instance
        repository: Repository for data access
    """

    def __init__(self, logger: logging.Logger, repository: Optional[Any] = None):
        """Initialize base service.
        
        Args:
            logger: Logger instance
            repository: Optional repository for data access
        """
        self.logger = logger
        self.repository = repository

    def _call_repository(
        self,
        func: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """Safely call repository method with error handling.
        
        Args:
            func: Repository function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from repository function
            
        Raises:
            DatabaseError: If repository operation fails
        """
        try:
            self.logger.debug(f"Calling repository method: {func.__name__}")
            result = func(*args, **kwargs)
            self.logger.debug(f"Repository operation successful: {func.__name__}")
            return result
        except FinSightException:
            raise
        except Exception as e:
            self.logger.error(
                f"Repository operation failed: {func.__name__}",
                exc_info=True,
                extra={"error": str(e)},
            )
            raise DatabaseError(
                f"Database operation failed: {str(e)}",
                details={"operation": func.__name__},
            )

    def _log_operation(
        self,
        operation: str,
        level: int = logging.INFO,
        **extra,
    ) -> None:
        """Log an operation with structured data.
        
        Args:
            operation: Operation description
            level: Log level
            **extra: Additional context data
        """
        self.logger.log(level, operation, extra=extra)


class CacheableService(BaseService[T]):
    """Service with caching support.
    
    Extends BaseService to add simple caching of results.
    """

    def __init__(self, logger: logging.Logger, repository: Optional[Any] = None):
        """Initialize cacheable service."""
        super().__init__(logger, repository)
        self._cache: dict = {}

    def get_cached(self, key: str) -> Optional[T]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        return self._cache.get(key)

    def set_cache(self, key: str, value: T) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        self.logger.debug(f"Cached value for key: {key}")

    def clear_cache(self, key: Optional[str] = None) -> None:
        """Clear cache.
        
        Args:
            key: Specific key to clear, or None to clear all
        """
        if key:
            self._cache.pop(key, None)
            self.logger.debug(f"Cleared cache for key: {key}")
        else:
            self._cache.clear()
            self.logger.debug("Cleared all cache")


class TransactionService(BaseService[T]):
    """Service with transaction support.
    
    Extends BaseService to add transaction handling.
    """

    def __init__(self, logger: logging.Logger, repository: Optional[Any] = None):
        """Initialize transaction service."""
        super().__init__(logger, repository)

    def execute_in_transaction(
        self,
        func: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """Execute function in a database transaction.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            DatabaseError: If transaction fails
        """
        try:
            self.logger.debug("Starting transaction")
            result = func(*args, **kwargs)
            self.logger.debug("Transaction completed successfully")
            return result
        except FinSightException:
            self.logger.warning("Transaction rolled back due to application error")
            raise
        except Exception as e:
            self.logger.error(
                "Transaction failed and rolled back",
                exc_info=True,
                extra={"error": str(e)},
            )
            raise DatabaseError(
                f"Transaction failed: {str(e)}",
            )
