from fastapi import HTTPException, status

class ConflictError(HTTPException):
    """Custom exception for resource conflicts (e.g., duplicate entry)."""
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

# You can define other custom exceptions here as needed
# class NotFoundError(HTTPException):
#     """Custom exception for resource not found."""
#     def __init__(self, detail: str = "Resource not found"):
#         super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)