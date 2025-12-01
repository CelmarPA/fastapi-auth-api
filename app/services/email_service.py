# app/services/email_service.py

"""
Email Service
-------------

Provides methods to send transactional emails:

- Password reset emails
- Email verification emails

Uses the Brevo (formerly Sendinblue) SMTP API for sending emails.
"""

import requests

from app.core.config import settings


class EmailService:
    """
    Service class responsible for sending emails.
    """

    @staticmethod
    def send_password_reset(to_email: str, token: str) -> bool:
        """
        Sends a password reset email to the specified recipient.

        :param to_email: Recipient email address.
        :type to_email: str

        :param token: Password reset token to include in the link.
        :type token: str

        :return: True if email was successfully sent, False otherwise.
        :rtype: bool
        """

        url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        payload = {
            "sender": {
                "name": "Auth API",
                "email": settings.MAIL_SENDER
            },
            "to": [
                {"email": to_email}
            ],
            "subject": "Password Reset Request",
            "htmlContent": f"""
                    <h2>Password Reset</h2>
                    <p>Click the link below to reset your password:</p>
                    <a href="{url}">Reset Password</a>
                    <p>This link expires in 15 minutes.</p>
                """
        }

        headers = {
            "api-key": settings.BREVO_API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers
        )

        return response.status_code == 201

    @staticmethod
    def send_verification_email(to_email: str, token: str) -> bool:
        """
        Sends an email verification email to the specified recipient.

        :param to_email: Recipient email address.
        :type to_email: str

        :param token: Verification token to include in the link.
        :type token: str

        :return: True if email was successfully sent, False otherwise.
        :rtype: bool
        """

        url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        payload = {
            "sender": {
                "name": "Auth API",
                "email": settings.MAIL_SENDER
            },
            "to": [
                {"email": to_email}
            ],
            "subject": "Verify Your Email Address",
            "htmlContent": f"""
                <h2>Email Verification</h2>
                <p>Click the link below to verify your email address:</p>
                <a href="{url}">Verify Email</a>
                <p>This link expires in 15 minutes.</p>
            """
        }

        headers = {
            "api-key": settings.BREVO_API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers
        )

        return response.status_code == 201
