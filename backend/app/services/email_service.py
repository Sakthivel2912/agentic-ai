"""Email delivery for account recovery messages."""
import asyncio
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode

from app.core.config import settings


def _send_message(message: EmailMessage) -> None:
    context = ssl.create_default_context()
    if settings.SMTP_USE_SSL:
        with smtplib.SMTP_SSL(
            settings.SMTP_HOST, settings.SMTP_PORT, context=context, timeout=15
        ) as server:
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
        return

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        if settings.SMTP_STARTTLS:
            server.starttls(context=context)
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(message)


async def send_password_reset_email(recipient: str, token: str) -> None:
    query = urlencode({"token": token})
    reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?{query}"
    message = EmailMessage()
    message["Subject"] = "Reset your AI Council password"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient
    message.set_content(
        "A password reset was requested for your AI Council account.\n\n"
        f"Use this one-time link within {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes:\n"
        f"{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )
    await asyncio.to_thread(_send_message, message)