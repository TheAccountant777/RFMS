from fastapi import HTTPException, status

class ConflictError(HTTPException):
    """Custom exception for resource conflicts (e.g., duplicate entry)."""
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class NotFoundError(HTTPException):
    """Custom exception for resource not found."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ValidationError(HTTPException):
    """Custom exception for validation errors."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)