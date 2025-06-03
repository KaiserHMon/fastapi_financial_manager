from pydantic import BaseModel, Field
import datetime
from enum import Enum

class EntryType(str, Enum):
    income = "income"
    expense = "expense"

class HistoryOut(BaseModel):
    history_id: int       
    user_id: int           
    item_id: int           
    type: EntryType
    amount: int            
    description: str       
    created_at: datetime
    
    class Config:
        orm_mode = True