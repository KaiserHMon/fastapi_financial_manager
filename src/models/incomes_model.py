from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.config.database import base

class IncomeModel(base):
    __tablename__ = 'incomes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    date: Mapped[int] = mapped_column(DateTime, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    user = relationship("UserModel", back_populates="incomes")
    category = relationship("CategoryModel", back_populates="incomes")