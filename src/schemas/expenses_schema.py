from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ExpenseIn(BaseModel):
    amount: float = Field(gt=0, description="Amount of the expense, must be greater than 0")
    description: str | None = Field(max_length=50, description="Description of the expense")
    date: datetime = Field(description="Date of the expense in ISO format (YYYY-MM-DD)")
    
class ExpenseOut(ExpenseIn):
    id: int
    category_id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
    
