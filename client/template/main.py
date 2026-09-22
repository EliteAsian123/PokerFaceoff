from websockets import ClientConnection, ConnectionClosed
from common.client_response import ClientResponse
from common.server_response import ServerResponse, ServerError, JoinSuccess, RoundStarting
from common.actions import Join
from websockets.asyncio.client import connect
from . import bot
import asyncio

async def send(ws: ClientConnection, model: ClientResponse):
    await ws.send(model.model_dump_json(), True)

async def recv(ws: ClientConnection) -> ServerResponse:
    response = await ws.recv()
    return ServerResponse.model_validate_json(response)

async def main():
    url: str = input("Enter PokerFaceoff server URL: ")
    try:
        async with connect(url) as ws:
            await send(ws, ClientResponse(action=Join(name=bot.BOT_NAME)))
            response = await recv(ws)
            match response.action:
                case ServerError(message=message):
                    print(f"Failed to connect to server: {message}")
                    return
                case JoinSuccess():
                    print("Successfully joined the server.")
                case _:
                    print("Unreachable.")
                    return

            while True:
                response = await recv(ws)
                match response.action:
                    case ServerError(message=message):
                        print(f"Server error: {message}")
                        return
                    case RoundStarting():
                        print("Starting round...")
                        bot.start_round()
                    case _:
                        print("Unreachable.")
                        return

    except ConnectionClosed:
        pass
    finally:
        pass

if __name__ == "__main__":
    asyncio.run(main())
