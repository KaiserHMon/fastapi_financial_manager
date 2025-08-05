from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..config.database import base

class UserModel(base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    categories = relationship("CategoryModel", back_populates="user")
    incomes = relationship("IncomeModel", back_populates="user")
    expenses = relationship("ExpenseModel", back_populates="user")
    histories = relationship("HistoryModel", back_populates="user")