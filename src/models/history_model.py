from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.config.database import base

class HistoryModel(base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    income_id: Mapped[int] = mapped_column(Integer, ForeignKey('incomes.id'), nullable=True, index=True)
    expense_id: Mapped[int] = mapped_column(Integer, ForeignKey('expenses.id'), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
