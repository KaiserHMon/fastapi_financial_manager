from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.config.database import base


class TokenDenylist(base):
    __tablename__ = 'token_denylist'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    jti: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    exp: Mapped[int] = mapped_column(Integer, nullable=False)
