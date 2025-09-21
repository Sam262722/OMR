"""
User-related Pydantic models for the OMR Evaluation System.
Handles user profiles, authentication, and role management.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class UserRole(str, Enum):
    """User role enumeration"""
    TEACHER = "teacher" 
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.TEACHER
    institution: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and len(v.replace(' ', '').replace('-', '').replace('+', '')) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v
    
    @validator('preferences')
    def validate_preferences(cls, v):
        # Ensure preferences is a valid dictionary
        if not isinstance(v, dict):
            return {}
        return v


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Model for updating user information"""
    full_name: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and len(v.replace(' ', '').replace('-', '').replace('+', '')) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v


class UserProfile(UserBase):
    """Complete user profile model"""
    id: UUID
    is_active: bool = True
    subscription_expires_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response model for API responses"""
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    institution: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription_tier: SubscriptionTier
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics model"""
    total_results: int = 0
    total_sessions: int = 0
    average_score: Optional[float] = None
    average_confidence: Optional[float] = None
    created_answer_keys: int = 0
    created_templates: int = 0
    last_processing_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserDashboard(BaseModel):
    """User dashboard data model"""
    user: UserResponse
    stats: UserStats
    recent_results: list = Field(default_factory=list)
    recent_sessions: list = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Model for password change requests"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserPreferences(BaseModel):
    """User preferences model"""
    theme: str = "light"
    language: str = "en"
    notifications: Dict[str, bool] = Field(default_factory=lambda: {
        "email_results": True,
        "email_sessions": True,
        "browser_notifications": True,
        "weekly_summary": False
    })
    dashboard_layout: Dict[str, Any] = Field(default_factory=dict)
    processing_defaults: Dict[str, Any] = Field(default_factory=lambda: {
        "confidence_threshold": 0.8,
        "auto_review": False,
        "batch_size": 10
    })
    
    @validator('theme')
    def validate_theme(cls, v):
        if v not in ['light', 'dark', 'auto']:
            raise ValueError('Theme must be light, dark, or auto')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        # Add supported languages as needed
        supported_languages = ['en', 'es', 'fr', 'de', 'zh', 'ja']
        if v not in supported_languages:
            raise ValueError(f'Language must be one of: {", ".join(supported_languages)}')
        return v


class UserInvitation(BaseModel):
    """Model for user invitations"""
    email: EmailStr
    role: UserRole = UserRole.TEACHER
    institution: Optional[str] = None
    department: Optional[str] = None
    message: Optional[str] = None
    expires_in_days: int = Field(default=7, ge=1, le=30)


class UserInvitationResponse(BaseModel):
    """Response model for user invitations"""
    id: UUID
    email: EmailStr
    role: UserRole
    institution: Optional[str] = None
    department: Optional[str] = None
    invited_by: UUID
    expires_at: datetime
    is_accepted: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class BulkUserImport(BaseModel):
    """Model for bulk user import"""
    users: list[UserCreate]
    send_invitations: bool = True
    default_role: UserRole = UserRole.TEACHER
    default_institution: Optional[str] = None
    
    @validator('users')
    def validate_users_list(cls, v):
        if len(v) == 0:
            raise ValueError('At least one user must be provided')
        if len(v) > 100:
            raise ValueError('Cannot import more than 100 users at once')
        return v


class UserSearchFilters(BaseModel):
    """Model for user search and filtering"""
    role: Optional[UserRole] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None
    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    search_term: Optional[str] = None  # Search in name, email, institution
    
    class Config:
        use_enum_values = True