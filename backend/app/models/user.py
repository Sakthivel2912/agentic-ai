"""
AI Council - User Model (SQLAlchemy)
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database.sqlite import Base
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    User Model (SQLAlchemy)
    """
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default=UserRole.USER)
    preferences = Column(Text, nullable=True, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        preferences = self.preferences
        if preferences is None:
            preferences = {}
        elif isinstance(preferences, str):
            try:
                import json
                preferences = json.loads(preferences)
            except (TypeError, ValueError):
                preferences = {}

        updated_at = self.updated_at or self.created_at or func.now()

        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "role": self.role,
            "preferences": preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else None,
        }


class PasswordResetToken(Base):
    """One-time password reset token stored by digest, never in plaintext."""
    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
