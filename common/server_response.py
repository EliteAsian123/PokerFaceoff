from common.public_game_state import PublicGameData
from typing import Literal
from pydantic import BaseModel, Field

class ServerError(BaseModel):
    type: Literal["serverError"] = "serverError"
    message: str

class JoinSuccess(BaseModel):
    type: Literal["joinSuccess"] = "joinSuccess"
    id: int

class RoundStarting(BaseModel):
    type: Literal["roundStarting"] = "roundStarting"
    data: PublicGameData

class YourTurn(BaseModel):
    type: Literal["yourTurn"] = "yourTurn"
    data: PublicGameData

class RoundEnd(BaseModel):
    type: Literal["roundEnd"] = "roundEnd"
    data: PublicGameData
    winners: list[int]

class IllegalAction(BaseModel):
    type: Literal["illegalAction"] = "illegalAction"
    message: str

class ServerResponse(BaseModel):
    action: ServerError | JoinSuccess | RoundStarting | YourTurn | RoundEnd | IllegalAction = Field(..., discriminator="type")
