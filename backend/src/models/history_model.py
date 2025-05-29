from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from config.database import engine, base
import datetime

class History(base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[int] = mapped_column(DateTime, nullable=False)
    income_id: Mapped[int] = mapped_column(Integer, ForeignKey('incomes.id'), nullable=False, index=True)
    expense_id: Mapped[int] = mapped_column(Integer, ForeignKey('expenses.id'), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
  
# Create the database tables
base.metadata.create_all(engine)