from common.public_game_state import PublicGameData, PublicPlayer
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
    winners: list[PublicPlayer]

class ServerResponse(BaseModel):
    action: ServerError | JoinSuccess | RoundStarting | YourTurn | RoundEnd = Field(..., discriminator="type")
