class AppError(Exception):
    """Base exception for application errors."""
    pass

class GeminiServiceError(AppError):
    """Raised when a Gemini API operation fails."""
    pass

class FileUploadError(AppError):
    """Raised when file upload or processing fails."""
    pass

class OperationTimeoutError(AppError):
    """Raised when an operation times out."""
    pass
