from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from config.database import engine, base


class TokenDenylist(base):
    __tablename__ = 'token_denylist'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    jti: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    exp: Mapped[int] = mapped_column(BigInteger, nullable=False) 
    
    
base.metadata.create_all(engine)