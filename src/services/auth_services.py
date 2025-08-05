from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas.token_schema import TokenData
from ..exceptions.http_errors import CREDENTIALS_EXCEPTION, INVALID_REFRESH_TOKEN
from ..services import user_services
from ..models.token_denylist_model import TokenDenylist
from ..models.user_model import UserModel
from ..dependencies import get_async_db

from datetime import timedelta
from typing import Annotated
from dotenv import load_dotenv
import os
import datetime
import uuid

from jose import JWTError, jwt


load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


oauth_bearer = OAuth2PasswordBearer(
    tokenUrl="login", scopes={"me": "Get user information"}
)


def create_access_token(token_data: TokenData) -> str:
    issued_at = int(token_data.issued_at.timestamp())
    exp = int(
        (
            token_data.issued_at + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        ).timestamp()
    )
    access_token = {
        "sub": token_data.username,
        "scopes": token_data.scopes,
        "iat": issued_at,
        "exp": exp,
        "token_type": "access",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(access_token, SECRET_KEY, JWT_ALGORITHM)


def create_refresh_token(token_data: TokenData) -> str:
    issued_at = int(token_data.issued_at.timestamp())
    exp = int(
        (token_data.issued_at + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
    )
    refresh_token = {
        "sub": token_data.username,
        "scopes": token_data.scopes,
        "iat": issued_at,
        "exp": exp,
        "token_type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(refresh_token, SECRET_KEY, JWT_ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise CREDENTIALS_EXCEPTION


async def add_token_to_denylist(db: AsyncSession, token: str):
    payload = decode_token(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    denylist_entry = TokenDenylist(jti=jti, exp=exp)
    db.add(denylist_entry)
    await db.commit()


async def auth_access_token(
    token: Annotated[str, Depends(oauth_bearer)],
    db: AsyncSession = Depends(get_async_db),
):
    payload = decode_token(token)
    username = payload.get("sub")
    token_type = payload.get("token_type")
    if not username or token_type != "access":
        raise CREDENTIALS_EXCEPTION
    user = await user_services.get_user(db, username)
    if not user:
        raise CREDENTIALS_EXCEPTION
    return user


async def auth_refresh_token(
    token: Annotated[str, Depends(oauth_bearer)],
    db: AsyncSession = Depends(get_async_db),
):
    payload = decode_token(token)
    username = payload.get("sub")
    token_type = payload.get("token_type")
    jti = payload.get("jti")

    if not username or token_type != "refresh":
        raise INVALID_REFRESH_TOKEN

    # Check if the token has been denylisted
    result = await db.execute(select(TokenDenylist).filter(TokenDenylist.jti == jti))
    if result.scalars().first():
        raise INVALID_REFRESH_TOKEN  # Token is denylisted

    new_access_token = TokenData(
        username=username,
        scopes=payload.get("scopes", []),
        issued_at=datetime.datetime.now(),
    )

    return create_access_token(new_access_token)
