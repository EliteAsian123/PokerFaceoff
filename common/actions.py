from typing import Literal
from pydantic import BaseModel

class Join(BaseModel):
    type: Literal["join"] = "join"
    name: str

class Fold(BaseModel):
    type: Literal["fold"] = "fold"

class Show(BaseModel):
    type: Literal["show"] = "show"

class Bet(BaseModel):
    type: Literal["bet"] = "bet"
    up_to: int

class AllIn(BaseModel):
    type: Literal["allIn"] = "allIn"

Action = Join | Fold | Show | Bet | AllIn
