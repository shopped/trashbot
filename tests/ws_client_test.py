import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://192.168.1.10:1337") as websocket:
        await websocket.send("trash")

asyncio.run(hello())
