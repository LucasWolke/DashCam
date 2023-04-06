import websockets
import asyncio
from ultralytics import YOLO
import json
import base64
import numpy as np
import cv2 as cv2

import time

model = YOLO("../models/detection/runs/detect/train2/weights/best.pt") #import yolov8 detection model

async def handler(websocket):
    while True:
        message = await websocket.recv()
        image = convert_image(message)
        bounding_boxes = detection(image)
        await websocket.send(json.dumps(bounding_boxes))
                
async def main():
    async with websockets.serve(handler, "192.168.0.45", 8001): # insert ipv4 address here
        await asyncio.Future()  # run forever


def detection(image):
    results = model(image)
    ret_arr = []
    for id2,result in enumerate(results):
        boxes = result.boxes
        for id,box in enumerate(boxes):  # get the vertices of the bounding box
            x1 = box.xyxy.cpu().numpy()[0][0]
            y1 = box.xyxy.cpu().numpy()[0][1]

            x2 = box.xyxy.cpu().numpy()[0][2]
            y2 = box.xyxy.cpu().numpy()[0][3]
    
            ret_str = str(x1) + "," + str(y1) +","+ str(x2) +","+ str(y2)
            print(ret_str)
            ret_arr.append(ret_str)
    return ret_arr

def classifiction(cropped_image):
    exit

def convert_image(image_base64):
    #bytes = base64.b64decode(image_base64)
    image_array = np.frombuffer(image_base64, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return img

if __name__ == "__main__":
    asyncio.run(main())