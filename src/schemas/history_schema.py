from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class HistoryOut(BaseModel):
    type: Literal['income', 'expense']
    amount: float
    description: str
    date: datetime
    category: str

