# Models package for OMR Evaluation System
# Contains Pydantic models for API requests, responses, and data validation

from .user_models import (
    UserProfile,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserRole,
    SubscriptionTier
)

from .omr_models import (
    OMRResult,
    OMRResultCreate,
    OMRResultUpdate,
    OMRResultResponse,
    ProcessingSession,
    ProcessingSessionCreate,
    ProcessingSessionUpdate,
    ProcessingSessionResponse,
    ProcessingStatus,
    ProcessingQuality
)

from .template_models import (
    OMRTemplate,
    OMRTemplateCreate,
    OMRTemplateUpdate,
    OMRTemplateResponse,
    AnswerKey,
    AnswerKeyCreate,
    AnswerKeyUpdate,
    AnswerKeyResponse
)

from .system_models import (
    SystemStats,
    SystemStatsResponse,
    HealthCheck,
    APIResponse,
    ErrorResponse,
    PaginatedResponse
)

from .file_models import (
    FileUpload,
    FileResponse,
    BatchUpload,
    BatchResponse,
    ProcessingConfig
)

__all__ = [
    # User models
    "UserProfile",
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    "UserRole",
    "SubscriptionTier",
    
    # OMR models
    "OMRResult",
    "OMRResultCreate",
    "OMRResultUpdate", 
    "OMRResultResponse",
    "ProcessingSession",
    "ProcessingSessionCreate",
    "ProcessingSessionUpdate",
    "ProcessingSessionResponse",
    "ProcessingStatus",
    "ProcessingQuality",
    
    # Template models
    "OMRTemplate",
    "OMRTemplateCreate",
    "OMRTemplateUpdate",
    "OMRTemplateResponse", 
    "AnswerKey",
    "AnswerKeyCreate",
    "AnswerKeyUpdate",
    "AnswerKeyResponse",
    
    # System models
    "SystemStats",
    "SystemStatsResponse",
    "HealthCheck",
    "APIResponse",
    "ErrorResponse",
    "PaginatedResponse",
    
    # File models
    "FileUpload",
    "FileResponse",
    "BatchUpload", 
    "BatchResponse",
    "ProcessingConfig"
]