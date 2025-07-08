from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped ,mapped_column
from src.config.database import base


class CategoryModel(base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    incomes = relationship("IncomeModel", back_populates="category")
    expenses = relationship("ExpenseModel", back_populates="category")
