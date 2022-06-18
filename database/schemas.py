from pydantic import BaseModel
from typing import List
from datetime import datetime


class LottoCreate(BaseModel):
    date: datetime
    result: List[int]
    is_last_day: bool


class Lotto(LottoCreate):
    id: int

    class Config:
        orm_mode = True
