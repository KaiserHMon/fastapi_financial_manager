from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal

class HistoryBase(BaseModel):
    type: Literal['income', 'expense']
    amount: float
    description: str
    date: datetime

class HistoryOut(HistoryBase):
    id: int
    category: str

    model_config = ConfigDict(from_attributes=True)