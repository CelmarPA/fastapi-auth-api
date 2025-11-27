import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sqlalchemy import Boolean

from .config import settings


def send_email(to: str, subject: str, html_content: str) -> Boolean:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to}],
        sender={
            "email": settings.EMAIL_FROM,
            "name": settings.EMAIL_FROM_NAME
        },
        subject=subject,
        html_content=html_content
    )

    try:
        api_instance.send_transac_email(email)
        return True

    except ApiException as e:
        print("Error sending email:", e)
        return False
