from websockets import ClientConnection
from common.client_response import *
from common.actions import *
from websockets.asyncio.client import connect
import asyncio

async def send(ws: ClientConnection, model: ClientResponse):
    await ws.send(model.model_dump_json(), True)

async def main():
    url: str = input("Enter server URL: ")
    async with connect(url) as ws:
        await send(ws, ClientResponse(action=Join(name="AJ")))
        response = await ws.recv()
        print(f"Received from server: {response}")
        await send(ws, ClientResponse(action=Join(name="AJ")))
        response = await ws.recv()
        print(f"Received from server: {response}")
        await send(ws, ClientResponse(action=Join(name="AJ")))
        response = await ws.recv()
        print(f"Received from server: {response}")

if __name__ == "__main__":
    asyncio.run(main())
