import hashlib
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.api.v1.endpoints import auth as auth_endpoint
from app.database.sqlite import Base
from app.models.user import PasswordResetToken, User
from app.schemas.user import PasswordResetConfirm, PasswordResetRequest
from app.services import auth_service
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_password_reset_uses_hashed_one_time_token(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'password-reset.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    sent_email = {}

    async def capture_reset_email(recipient: str, token: str) -> None:
        sent_email.update({"recipient": recipient, "token": token})

    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test")
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", "no-reply@example.com")
    monkeypatch.setattr(auth_service, "send_password_reset_email", capture_reset_email)

    async with session_factory() as db:
        user = User(
            id="reset-user",
            email="reset@example.com",
            full_name="Reset User",
            hashed_password=get_password_hash("OriginalPassword123"),
            is_active=True,
        )
        db.add(user)
        await db.commit()

        await AuthService.request_password_reset("unknown@example.com", db)
        assert sent_email == {}
        result = await db.execute(select(PasswordResetToken))
        assert result.scalars().all() == []

        await AuthService.request_password_reset(user.email, db)
        result = await db.execute(select(PasswordResetToken))
        token_record = result.scalar_one()
        raw_token = sent_email["token"]
        assert sent_email["recipient"] == user.email
        assert token_record.token_hash == hashlib.sha256(raw_token.encode()).hexdigest()
        assert token_record.token_hash != raw_token

        await AuthService.reset_password(
            raw_token,
            "ReplacementPassword123",
            "ReplacementPassword123",
            db,
        )
        await db.refresh(user)
        assert verify_password("ReplacementPassword123", user.hashed_password)

        with pytest.raises(HTTPException) as error:
            await AuthService.reset_password(
                raw_token,
                "AnotherPassword123",
                "AnotherPassword123",
                db,
            )
        assert error.value.status_code == 400

    await engine.dispose()


@pytest.mark.asyncio
async def test_debug_reset_request_returns_token_without_smtp(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'password-reset-debug.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(settings, "SMTP_HOST", "")
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", "")

    async with session_factory() as db:
        db.add(User(
            id="debug-reset-user",
            email="debug-reset@example.com",
            full_name="Debug Reset User",
            hashed_password=get_password_hash("OriginalPassword123"),
            is_active=True,
        ))
        await db.commit()

        token = await AuthService.request_password_reset(
            "debug-reset@example.com", db, allow_test_token=True
        )

        assert token
        await AuthService.reset_password(
            token, "TestingPassword123", "TestingPassword123", db
        )

    await engine.dispose()


@pytest.mark.asyncio
async def test_forgot_password_endpoint_returns_working_debug_link(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'password-reset-api.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(settings, "SMTP_HOST", "")
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", "")
    monkeypatch.setattr(settings, "DEBUG", True)
    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:5173")
    monkeypatch.setattr(auth_endpoint.sqlite, "get_session", session_factory)

    async with session_factory() as db:
        db.add(User(
            id="endpoint-reset-user",
            email="endpoint-reset@example.com",
            full_name="Endpoint Reset User",
            hashed_password=get_password_hash("OriginalPassword123"),
            is_active=True,
        ))
        await db.commit()

    request_result = await auth_endpoint.forgot_password(
        PasswordResetRequest(email="endpoint-reset@example.com")
    )
    reset_url = request_result.data["reset_url"]
    token = parse_qs(urlparse(reset_url).query)["token"][0]
    assert reset_url.startswith("http://localhost:5173/reset-password?")

    reset_result = await auth_endpoint.reset_password(
        PasswordResetConfirm(
            token=token,
            new_password="EndpointPassword123",
            confirm_password="EndpointPassword123",
        )
    )
    assert reset_result.message.startswith("Password reset successfully")

    await engine.dispose()