from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class CategoryType(str, Enum):
    INCOME = 'income'
    EXPENSE = 'expense'


class CategoriesIn(BaseModel):
    name: str = Field(max_length=50)
    type: CategoryType
    
    
class CategoriesOut(BaseModel):
    id: int
    name: str = Field(max_length=50)
    type: CategoryType
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)