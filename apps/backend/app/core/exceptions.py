from fastapi import HTTPException, status
from typing import Any


class AppException(HTTPException):
    """Base application exception."""
    
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": code,
                    "message": message,
                    "details": self.details,
                }
            },
        )


class ValidationError(AppException):
    """Validation error."""
    
    def __init__(self, message: str, details: list[Any] | None = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class AuthenticationError(AppException):
    """Authentication error."""
    
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTHENTICATION_ERROR",
            message=message,
        )


class AuthorizationError(AppException):
    """Authorization error."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="AUTHORIZATION_ERROR",
            message=message,
        )


class NotFoundError(AppException):
    """Resource not found error."""
    
    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message,
        )


class ConflictError(AppException):
    """Conflict error (e.g., duplicate resource)."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=message,
        )


class BusinessRuleError(AppException):
    """Business rule violation."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BUSINESS_RULE_ERROR",
            message=message,
        )
