import websockets
import asyncio

async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)
        await websocket.send("generic response")
                
async def main():
    async with websockets.serve(handler, "192.168.0.45", 8001): # insert ipv4 address here
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())