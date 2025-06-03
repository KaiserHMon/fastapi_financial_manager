from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped ,mapped_column
from config.database import engine, base


class CategoryModel(base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    type: Mapped[str] = mapped_column(String, nullable=False)  # 'income' or 'expense'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    incomes = relationship("Income", back_populates="Category")
    expenses = relationship("Expense", back_populates="Category")
    
    
# Create the database tables
base.metadata.create_all(engine)