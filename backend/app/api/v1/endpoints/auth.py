"""
AI Council - Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserUpdate,
    PasswordChange,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.database.sqlite import sqlite
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/forgot-password", response_model=SuccessResponse)
async def forgot_password(request_data: PasswordResetRequest):
    """Send a reset link when the account exists, without confirming account existence."""
    db = sqlite.get_session()
    try:
        testing_token = await AuthService.request_password_reset(
            request_data.email,
            db,
            allow_test_token=settings.DEBUG and not (settings.SMTP_HOST and settings.SMTP_FROM_EMAIL),
        )
        if settings.DEBUG and testing_token:
            reset_url = (
                f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={testing_token}"
            )
            return SuccessResponse(
                message="Testing reset link created.",
                data={"reset_url": reset_url},
            )
        return SuccessResponse(
            message="If an active account matches that email, a reset link will be sent."
        )
    finally:
        await db.close()


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(request_data: PasswordResetConfirm):
    """Set a new password using a valid one-time reset token."""
    db = sqlite.get_session()
    try:
        await AuthService.reset_password(
            request_data.token,
            request_data.new_password,
            request_data.confirm_password,
            db,
        )
        return SuccessResponse(message="Password reset successfully. You can now sign in.")
    finally:
        await db.close()


@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user
    
    - **full_name**: User's full name
    - **email**: User's email address (must be unique)
    - **password**: User's password (min 8 characters)
    - **confirm_password**: Password confirmation (must match password)
    """
    try:
        db = sqlite.get_session()
        user = await AuthService.register_user(user_data, db)
        await db.close()
        return SuccessResponse(
            message="User registered successfully",
            data={"user": user.model_dump()}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """
    Login user and return access token
    
    - **email**: User's email address
    - **password**: User's password
    """
    try:
        db = sqlite.get_session()
        result = await AuthService.authenticate_user(user_data, db)
        await db.close()
        return TokenResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/login/form", response_model=TokenResponse)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user using OAuth2 form (for Swagger UI)
    
    - **username**: Email address
    - **password**: Password
    """
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    return await login(user_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user information
    
    Requires valid JWT token in Authorization header
    """
    try:
        db = sqlite.get_session()
        user = await AuthService.get_current_user(token, db)
        await db.close()
        return UserResponse(**user.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.patch("/me", response_model=SuccessResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current authenticated user information
    
    - **full_name**: Updated full name (optional)
    - **email**: Updated email (optional)
    - **preferences**: User preferences (optional)
    """
    try:
        db = sqlite.get_session()
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        updated_user = await AuthService.update_user(str(current_user.id), update_dict, db)
        await db.close()
        return SuccessResponse(
            message="User updated successfully",
            data={"user": updated_user.model_dump()}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """
    Change current user's password
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 characters)
    - **confirm_password**: New password confirmation
    """
    try:
        db = sqlite.get_session()
        password_dict = {
            "current_password": password_data.current_password,
            "new_password": password_data.new_password,
            "confirm_password": password_data.confirm_password
        }
        await AuthService.change_password(str(current_user.id), password_dict, db)
        await db.close()
        return SuccessResponse(message="Password changed successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client-side token removal)
    
    Note: JWT tokens are stateless, so this is mainly for client-side cleanup
    """
    try:
        return SuccessResponse(message="Logged out successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
