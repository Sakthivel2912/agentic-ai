"""
AI Council - Authentication Service (SQLite)
"""
from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import PasswordResetToken, User
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.core.security import verify_password, create_access_token, decode_access_token, get_password_hash
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.email_service import send_password_reset_email
import logging
import uuid

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service (SQLite)"""

    @staticmethod
    async def request_password_reset(
        email: str,
        db: AsyncSession,
        allow_test_token: bool = False,
    ) -> Optional[str]:
        """Create a reset token and optionally return it for local testing."""
        email_configured = bool(settings.SMTP_HOST and settings.SMTP_FROM_EMAIL)
        if not email_configured and not allow_test_token:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Password reset email is not configured",
            )

        result = await db.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            return None

        now = datetime.utcnow()
        await db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
        token = secrets.token_urlsafe(32)
        token_record = PasswordResetToken(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            expires_at=now + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
        )
        db.add(token_record)
        await db.commit()

        if not email_configured:
            return token

        try:
            await send_password_reset_email(user.email, token)
        except Exception:
            await db.execute(
                update(PasswordResetToken)
                .where(PasswordResetToken.id == token_record.id)
                .values(used_at=datetime.utcnow())
            )
            await db.commit()
            logger.exception("Password reset email delivery failed")
        return None

    @staticmethod
    async def reset_password(token: str, new_password: str, confirm_password: str, db: AsyncSession) -> None:
        """Consume a valid reset token and replace the associated password."""
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match",
            )

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.utcnow(),
            )
        )
        token_record = result.scalar_one_or_none()
        if token_record is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link is invalid or expired",
            )

        result = await db.execute(select(User).where(User.id == token_record.user_id))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link is invalid or expired",
            )

        now = datetime.utcnow()
        consumed = await db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.id == token_record.id,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
            .values(used_at=now)
        )
        if consumed.rowcount != 1:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link is invalid or expired",
            )

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = now
        await db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.id != token_record.id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
        await db.commit()
    
    @staticmethod
    async def register_user(user_data: UserRegister, db: AsyncSession) -> UserResponse:
        """
        Register a new user
        
        Args:
            user_data: User registration data
            db: Database session
            
        Returns:
            Created user response
            
        Raises:
            HTTPException: If user already exists or validation fails
        """
        # Validate password match
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        try:
            user = User(
                id=str(uuid.uuid4()),
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=get_password_hash(user_data.password),
                is_active=True,
                is_superuser=False,
                role="user"
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"User registered successfully: {user.email}")
            return UserResponse(**user.to_dict())
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    @staticmethod
    async def authenticate_user(user_data: UserLogin, db: AsyncSession) -> Dict[str, Any]:
        """
        Authenticate user and return token
        
        Args:
            user_data: User login data
            db: Database session
            
        Returns:
            Dictionary with access token and user data
            
        Raises:
            HTTPException: If authentication fails
        """
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        # Update last login timestamp
        user.updated_at = datetime.utcnow()
        await db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        logger.info(f"User authenticated successfully: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(**user.to_dict())
        }
    
    @staticmethod
    async def get_current_user(token: str, db: AsyncSession) -> User:
        """
        Get current user from JWT token
        
        Args:
            token: JWT access token
            db: Database session
            
        Returns:
            User object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        try:
            payload = decode_access_token(token)
            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is deactivated"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    
    @staticmethod
    async def update_user(user_id: str, update_data: Dict[str, Any], db: AsyncSession) -> UserResponse:
        """
        Update user information
        
        Args:
            user_id: User ID
            update_data: Data to update
            db: Database session
            
        Returns:
            Updated user response
            
        Raises:
            HTTPException: If user not found or update fails
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User updated successfully: {user.email}")
        return UserResponse(**user.to_dict())
    
    @staticmethod
    async def change_password(user_id: str, password_data: Dict[str, str], db: AsyncSession) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            password_data: Password change data
            db: Database session
            
        Returns:
            True if successful
            
        Raises:
            HTTPException: If validation fails or user not found
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_data["current_password"], user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password match
        if password_data["new_password"] != password_data["confirm_password"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match"
            )
        
        # Update password
        user.hashed_password = get_password_hash(password_data["new_password"])
        user.updated_at = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Password changed successfully for user: {user.email}")
        return True
