from common.actions import Action
from pydantic import BaseModel, Field

class ClientResponse(BaseModel):
    action: Action = Field(..., discriminator="type")
