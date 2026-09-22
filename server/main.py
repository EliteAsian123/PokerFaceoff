from server.server import Server
import asyncio
import sys

async def main():
    expected_player_count = int(sys.argv[1])
    server = Server()
    await server.start(expected_player_count, True)

if __name__ == "__main__":
    asyncio.run(main())
