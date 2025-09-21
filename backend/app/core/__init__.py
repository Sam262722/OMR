"""
Core application modules for the OMR Evaluation System backend.
"""

from .config import get_settings
from .security import verify_token, get_current_user
from .database import db_manager, init_db

__all__ = [
    "get_settings",
    "verify_token", 
    "get_current_user",
    "db_manager",
    "init_db"
]