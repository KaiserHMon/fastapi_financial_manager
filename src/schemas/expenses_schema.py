from pydantic import BaseModel, Field
import datetime

class ExpensesIn(BaseModel):
    amount: float = Field(gt=0, description="Amount of the income, must be greater than 0")
    description: str | None = Field(max_length=50, description="Description of the income")
    date: datetime.datetime = Field(description="Date of the income in ISO format (YYYY-MM-DD)")
    
class ExpensesOut(ExpensesIn):
    id: int
    category_id: int
    user_id: int
    
    class Config:
        from_attributes = True
    
