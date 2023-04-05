import websockets
import asyncio

async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)
        await websocket.send("generic response")
        image = convert_image(message)
                
async def main():
    async with websockets.serve(handler, "192.168.0.45", 8001): # insert ipv4 address here
        await asyncio.Future()  # run forever


def convert_image(image_base64):
    bytes = base64.b64decode(image_base64)
    image_array = np.frombuffer(bytes, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return img

if __name__ == "__main__":
    asyncio.run(main())