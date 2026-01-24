# ============================================================================
# ProInvestiX Enterprise API - Custom Exceptions
# ============================================================================

from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class ProInvestiXException(HTTPException):
    """Base exception for ProInvestiX API."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


# =============================================================================
# AUTHENTICATION EXCEPTIONS
# =============================================================================

class InvalidCredentialsException(ProInvestiXException):
    """Raised when login credentials are invalid."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            error_code="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredException(ProInvestiXException):
    """Raised when JWT token has expired."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            error_code="TOKEN_EXPIRED",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenException(ProInvestiXException):
    """Raised when JWT token is invalid."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            error_code="INVALID_TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InsufficientPermissionsException(ProInvestiXException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, required_role: str = None):
        detail = "Insufficient permissions"
        if required_role:
            detail = f"Insufficient permissions. Required role: {required_role}"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="INSUFFICIENT_PERMISSIONS",
        )


# =============================================================================
# RESOURCE EXCEPTIONS
# =============================================================================

class NotFoundException(ProInvestiXException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with ID '{resource_id}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
        )


class AlreadyExistsException(ProInvestiXException):
    """Raised when trying to create a resource that already exists."""
    
    def __init__(self, resource: str = "Resource", field: str = None, value: Any = None):
        detail = f"{resource} already exists"
        if field and value:
            detail = f"{resource} with {field} '{value}' already exists"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="ALREADY_EXISTS",
        )


class ValidationException(ProInvestiXException):
    """Raised when validation fails."""
    
    def __init__(self, detail: str = "Validation failed", errors: list = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )
        self.errors = errors or []


# =============================================================================
# BUSINESS LOGIC EXCEPTIONS
# =============================================================================

class BusinessLogicException(ProInvestiXException):
    """Raised when a business rule is violated."""
    
    def __init__(self, detail: str, error_code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
        )


class InsufficientBalanceException(BusinessLogicException):
    """Raised when wallet has insufficient balance."""
    
    def __init__(self, required: float, available: float):
        super().__init__(
            detail=f"Insufficient balance. Required: {required}, Available: {available}",
            error_code="INSUFFICIENT_BALANCE",
        )


class EventSoldOutException(BusinessLogicException):
    """Raised when an event is sold out."""
    
    def __init__(self, event_name: str = None):
        detail = "Event is sold out"
        if event_name:
            detail = f"Event '{event_name}' is sold out"
        super().__init__(
            detail=detail,
            error_code="EVENT_SOLD_OUT",
        )


class TicketAlreadyUsedException(BusinessLogicException):
    """Raised when a ticket has already been used."""
    
    def __init__(self, ticket_hash: str = None):
        detail = "Ticket has already been used"
        if ticket_hash:
            detail = f"Ticket '{ticket_hash}' has already been used"
        super().__init__(
            detail=detail,
            error_code="TICKET_ALREADY_USED",
        )
