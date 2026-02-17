from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import settings


def _send_email(to_email: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.send_message(msg)


def send_activation_email(email: str, token: str) -> None:
    link = f"http://localhost:8000/api/v1/accounts/activate?token={token}"
    _send_email(
        to_email=email,
        subject="Activate your account",
        body=f"Welcome!\n\nActivate your account using this link:\n{link}\n\nThis link expires in 24 hours.",
    )


def send_password_reset_email(email: str, token: str) -> None:
    link = f"http://localhost:8000/api/v1/accounts/reset-password?token={token}"
    _send_email(
        to_email=email,
        subject="Password reset",
        body=f"You requested a password reset.\n\nUse this link to set a new password:\n{link}\n\nIf you did not request this, ignore this email.",
    )


def send_payment_confirmation_email(email: str, order_id: int, amount: str) -> None:
    _send_email(
        to_email=email,
        subject="Payment confirmation",
        body=f"Thanks for your purchase!\n\nOrder #{order_id} is paid.\nAmount: {amount}\n",
    )


def send_payment_confirmation_email(email: str, order_id: int, amount: str) -> None:
    # Temporary stub (MailHog/SMTP later)
    print(f"[EMAIL] Payment confirmation for {email}: Order #{order_id} paid, amount: {amount}")
