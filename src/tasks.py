from __future__ import annotations
from sqlalchemy import delete
from .models.token_denylist_model import TokenDenylist
from .dependencies import get_async_db
import datetime
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .config.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

async def cleanup_expired_tokens():
    async for db in get_async_db():
        async with db as session:
            await session.execute(
                delete(TokenDenylist).where(TokenDenylist.exp < datetime.datetime.now())
            )
            await session.commit()


async def send_password_reset_email(email: str, token: str):
    html = f"""<p>Hi, this is your link to reset your password</p> 
    <p>http://localhost:8080/reset-password?token={token}</p>"""

    message = MessageSchema(
        subject="Reset your password",
        recipients=[email],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)