from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class IncomeIn(BaseModel):
    amount: float = Field(gt=0, description="Amount of the income, must be greater than 0")
    description: str | None = Field(max_length=50, description="Description of the income")
    date: datetime = Field(description="Date of the income in ISO format (YYYY-MM-DD)")
    category_id: int = Field(description="Category of the income")
    
class IncomeOut(IncomeIn):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

    