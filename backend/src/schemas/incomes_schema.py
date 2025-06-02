from pydantic import BaseModel, Field
from typing import Optional
import datetime

class IncomeIn(BaseModel):
    amount: float = Field(gt=0, description="Amount of the income, must be greater than 0")
    description: Optional[str] = None, Field(max_length=50, description="Description of the income")
    date: datetime = Field(description="Date of the income in ISO format (YYYY-MM-DD)")
    
class IncomeOut(IncomeIn):
    id: int
    category_id: int
    user_id: int
    

    