class HackRxException(Exception):
    """Base exception for HackRx system."""
    pass

class DocumentProcessingError(HackRxException):
    """Exception raised when document processing fails."""
    pass

class EmbeddingError(HackRxException):
    """Exception raised when embedding generation fails."""
    pass

class LLMServiceError(HackRxException):
    """Exception raised when LLM service fails."""
    pass

class RetrievalError(HackRxException):
    """Exception raised when document retrieval fails."""
    pass

class ValidationError(HackRxException):
    """Exception raised when input validation fails."""
    pass

class ConfigurationError(HackRxException):
    """Exception raised when configuration is invalid."""
    pass

class APIError(HackRxException):
    """Exception raised when external API calls fail."""
    pass 