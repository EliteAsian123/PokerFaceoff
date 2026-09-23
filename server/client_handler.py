from __future__ import annotations
from typing import TYPE_CHECKING

# We only need these for type checking. Prevents circular imports.
if TYPE_CHECKING:
    from server.server import Server

from common.client_response import ClientResponse
from common.server_response import RoundStarting, ServerResponse, JoinSuccess, ServerError
from common.actions import Join
from server.player import Player
from server.server_state import ServerState
from server.logger import log_important
from websockets import ServerConnection, ConnectionClosed

class ClientHandler:
    player: Player | None
    id: int
    ws: ServerConnection

    def __init__(self, id: int, ws: ServerConnection):
        self.player = None
        self.id = id
        self.ws = ws

    async def send(self, model: ServerResponse):
        await self.ws.send(model.model_dump_json(), True)

    async def __handle_lobby(self, server: Server, data: ClientResponse):
        match data.action:
            case Join(name=name):
                if self.player != None:
                    raise ValueError(f"You have already joined!")

                player = Player(self.ws, self.id, name)
                server.add_player(player)

                log_important(f"Connection {self.ws.remote_address} joined as '{name}'")
                await self.send(ServerResponse(action=JoinSuccess(id=self.id)))
            case _:
                raise ValueError("You must join before performing any action.")

    async def start_handler(self, server: Server):
        log_important(f"Connnection opened with {self.ws.local_address}")

        try:
            async for raw_message in self.ws:
                data = ClientResponse.model_validate_json(raw_message)
                match server.state:
                    case ServerState.LOBBY:
                        await self.__handle_lobby(server, data)
        except ConnectionClosed:
            if self.player == None:
                log_important(f"Connnection closed with {self.ws.remote_address}")
            else:
                log_important(f"Connnection closed with {self.ws.remote_address} '{self.player.data.name}'")
                server.queue_player_removal(self.player)
        except Exception as e:
            if self.player == None:
                log_important(f"Error with {self.ws.remote_address}: {e}")
            else:
                log_important(f"Error with {self.ws.remote_address} '{self.player.data.name}': {e}")
                server.queue_player_removal(self.player)

            try:
                await self.send(ServerResponse(action=ServerError(message=str(e))))
                await self.ws.close()
            except:
                pass
        finally:
            server.disconnect_client_handler(self)
