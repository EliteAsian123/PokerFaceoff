from websockets import ClientConnection, ConnectionClosed
from common.client_response import ClientResponse
from common.public_game_state import PublicGameData, PublicPlayer
from common.server_response import ServerResponse, ServerError, JoinSuccess, RoundStarting
from common.actions import Join
from websockets.asyncio.client import connect
from . import bot
import asyncio
import sys

async def send(ws: ClientConnection, model: ClientResponse):
    await ws.send(model.model_dump_json(), True)

async def recv(ws: ClientConnection) -> ServerResponse:
    response = await ws.recv()
    return ServerResponse.model_validate_json(response)

def get_me(data: PublicGameData, self_id: int) -> PublicPlayer:
    for p in data.players:
        if p.id == self_id:
            return p
    raise ValueError(f"Could not find player data with ID {self_id} in game data.")

async def main():
    bot.pre_join()

    url: str
    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        url = input("Enter PokerFaceoff server URL: ")

    self_id: int = -1
    try:
        async with connect(url) as ws:
            await send(ws, ClientResponse(action=Join(name=bot.DISPLAY_NAME)))
            response = await recv(ws)
            match response.action:
                case ServerError(message=message):
                    print(f"Failed to connect to server: {message}")
                    return
                case JoinSuccess(id=id):
                    self_id = id
                    print(f"Successfully joined the server with ID {self_id}")
                case _:
                    print("Unreachable")
                    return

            while True:
                response = await recv(ws)
                match response.action:
                    case ServerError(message=message):
                        print(f"Server error: {message}")
                        return
                    case RoundStarting(data=data):
                        print("Starting round...")
                        bot.start_round(data, get_me(data, self_id))
                    case _:
                        print("Unreachable")
                        return

    except ConnectionClosed:
        pass
    finally:
        pass

if __name__ == "__main__":
    asyncio.run(main())
