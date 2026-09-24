import pytest
from sqlalchemy import text

from app.database.sqlite import AsyncSessionLocal
from app.schemas.user import UserRegister
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_user_returns_valid_response():
    async with AsyncSessionLocal() as db:
        await db.execute(text("DELETE FROM users"))
        await db.commit()

        user_data = UserRegister(
            full_name="Test User",
            email="register-regression@example.com",
            password="Password123",
            confirm_password="Password123",
        )

        result = await AuthService.register_user(user_data, db)

        assert result.email == user_data.email
        assert result.full_name == user_data.full_name
        assert result.updated_at is not None
