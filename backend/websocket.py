from typing import Counter
import websockets
import asyncio
from ultralytics import YOLO
import json
import base64
import numpy as np
import cv2 as cv2

import time

import random

import numpy as np
import os
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
from csv import reader
import threading

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(10)

modelDetection = tf.keras.models.load_model('../models/classification/less-simple-classification-model2', compile=False)
modelDetection.compile()

model = YOLO("../models/detection/runs/detect/train9/weights/best.pt") #import yolov8 detection model

print("websocket ready")

async def handler(websocket):
        while True:
            message = await websocket.recv() 
            image = convert_image(message)
            response = detection(image)
            response = (json.dumps(response))
            await websocket.send(response)                

async def main():
    async with websockets.serve(handler, "192.168.0.45", 8001): # insert ipv4 address here
        await asyncio.Future()  # run forever

def detection(image):
    results = model(image)
    ret_arr = []
    label_arr = []
    for id2,result in enumerate(results):
        boxes = result.boxes
        for id,box in enumerate(boxes):  # get the vertices of the bounding box
            x1 = box.xyxy.cpu().numpy()[0][0]
            y1 = box.xyxy.cpu().numpy()[0][1]

            x2 = box.xyxy.cpu().numpy()[0][2]
            y2 = box.xyxy.cpu().numpy()[0][3]

            if(x2 - x1 < 30 and y2 - y1 < 30): # very small results are mostly wrong, so we disregard them
                continue

            crop_img = image[int(y1):int(y2), int(x1):int(x2)]
            label = classification(crop_img)

            if(label == -1): # -1 if probabilty too low
                continue
            
            label_arr.append(label)
            ret_str = str(x1) + "," + str(y1) +","+ str(x2) +","+ str(y2)
            ret_arr.append(ret_str)

    print([ret_arr, list(set(label_arr))])  
    return [ret_arr, list(set(label_arr))]

def classification(image):
    image = preprocess_detection(image)
    img_array = [tf.expand_dims(image, 0)]
    predictions = modelDetection.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    max_prob = np.max(score.numpy())

    if max_prob > 0.85: # when the model is not more than 85% sure about its prediction we disregard its prediction (might need to tweak the amount!)
        return int(np.argmax(score))
    else:
        return -1

def preprocess_detection(image): # preprocessing depends on model implementation! (grayscale + equalisation + normalisation)
    image = Image.fromarray(image)
    image = ImageOps.grayscale(image)
    image = ImageOps.equalize(image, mask = None)
    image = image.resize((32,32))
    image = np.array(image) 
    im = Image.fromarray(image)
    image = image / 255.0
    return image

def convert_image(image_bytes):
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return img

if __name__ == "__main__":
    asyncio.run(main())