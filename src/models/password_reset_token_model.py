from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import base
import datetime

class PasswordResetToken(base):
    __tablename__ = "password_reset_tokens"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=False)
    from .user_model import UserModel
    user = relationship("UserModel")
