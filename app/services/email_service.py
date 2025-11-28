import requests

from app.core.config import settings


class EmailService:

    @staticmethod
    def send_password_reset(to_email: str, token: str):
        url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        payload = {
            "sender": {"name": "Auth API", "email": settings.MAIL_SENDER},
            "to": [{"email": to_email}],
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
