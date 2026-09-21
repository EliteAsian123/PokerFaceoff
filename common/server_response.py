from typing import Literal
from pydantic import BaseModel, Field

class ServerError(BaseModel):
    type: Literal["serverError"] = "serverError"
    message: str

class JoinSuccess(BaseModel):
    type: Literal["joinSuccess"] = "joinSuccess"

class RoundStarting(BaseModel):
    type: Literal["roundStarting"] = "roundStarting"

class ServerResponse(BaseModel):
    action: ServerError | JoinSuccess | RoundStarting = Field(..., discriminator="type")
