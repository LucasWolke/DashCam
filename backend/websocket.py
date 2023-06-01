from typing import Counter
import websockets
import asyncio
from ultralytics import YOLO
import json
import base64
import cv2 as cv2
import time
import random
import numpy as np
import os
from PIL import Image, ImageOps
import tensorflow as tf

from concurrent.futures import ThreadPoolExecutor, wait

model_classification = tf.keras.models.load_model('../models/classification/classification-model-1', compile=False)
model_classification.compile()

model_validity = tf.keras.models.load_model('../models/validity/validity-model-checkpoint', compile=False)
model_validity.compile()

model_detection = YOLO("../models/detection/runs/detect/train9/weights/best.pt") #import yolov8 detection model

print("websocket ready")

new_labels = []
valid_labels = []

count = 0

detection_results = []

async def handler(websocket):
    while True:
            global valid_labels
            global new_labels
            image = await websocket.recv()
            image = convert_image(image)
            response = detection(image)
            response = (json.dumps(response))
            await websocket.send(response)
            new_labels = []

async def main():
    async with websockets.serve(handler, "192.168.0.45", 8001): # insert ipv4 address here
        await asyncio.Future()

def detection(image):
    results = model_detection(image, conf=0.75)
    global valid_labels
    global new_labels
    images = []
    ret_arr = []
    for result in results:
        boxes = result.boxes
        for box in boxes:  # get the vertices of the bounding box
            x1 = box.xyxy.cpu().numpy()[0][0]
            y1 = box.xyxy.cpu().numpy()[0][1]

            x2 = box.xyxy.cpu().numpy()[0][2]
            y2 = box.xyxy.cpu().numpy()[0][3]
            
            ret_str = str(x1) + "," + str(y1) +","+ str(x2) +","+ str(y2)
            ret_arr.append(ret_str)

            images.append(preprocess_classification(image, y1, y2, x1, x2))

        new_labels = classification(images)
        
        valid_labels = validation(list(set(new_labels)))

        return ([ret_arr, valid_labels])

def validation(new_labels):
    global valid_labels
    if (len(new_labels) == 0 and len(valid_labels) == 0):
        return []
    if len(new_labels) == 0: # if there are no new labels we add 43, which stands for no traffic sign
        new_labels.append(43)
    if len(valid_labels) == 0:
        valid_labels.append(43)
    label_combinations = []
    for x in valid_labels: # create all label combinations of sign1's and sign2's
        for y in new_labels:
            input = (int(x),int(y))
            arr = np.expand_dims(input, axis=0)
            label_combinations.append(arr)

    if(len(label_combinations) == 0):
            return []    

    with tf.device("gpu:0"):
        predictions = model_validity.predict(np.vstack(label_combinations))

    processed_predictions = validation_process_prediction(predictions, label_combinations)

    valid_signs = processed_predictions[0] # all valid signs will be added here

    return(valid_signs)

def validation_process_prediction(predictions, label_combinations):
    valid_signs = [] # all valid signs will be added here
    remove = [] # all invalid signs

    for x,prediction in enumerate(predictions):
            score = (np.argmax(tf.nn.softmax(prediction)))
            label_combinations2 = label_combinations[x][0]

            if int(score) == 0: # sign2 replaces sign1
                remove.append(int(label_combinations2[0]))
                valid_signs.append(int(label_combinations2[1]))
            elif int(score) == 1: # both signs valid
                valid_signs.append(int(label_combinations2[0]))
                valid_signs.append(int(label_combinations2[1]))
            elif int(score) == 2: # no signs valid
                remove.append(int(label_combinations2[0]))
                remove.append(int(label_combinations2[1]))
            else: # sign1 stays valid, sign2 invalid
                valid_signs.append(int(label_combinations2[0]))
                remove.append(int(label_combinations2[1]))

    remove = list(set(remove)) # removes all duplicate elements 
    valid_signs = list(set(valid_signs))

    for x in remove: # remove all invalid signs
        if x in valid_signs and not (x >= 11 and x <= 40 and x != 12): # never remove "only on sight valid" signs
            valid_signs.remove(x)                                      # ^ workaround so model is less complex ^

    return [valid_signs]

def classification(images):

    new_labels = []
    if(len(images) == 0):
        return new_labels
    
    with tf.device("gpu:0"):
        predictions = model_classification.predict(np.vstack(images))

    for prediction in predictions:
        score = tf.nn.softmax(prediction)
        max_prob = np.max(score.numpy())
        if max_prob < 0.75: # when the model is not more than 75% sure about its prediction we disregard its prediction (might need to tweak the amount!)
            continue
        new_labels.append(int(np.argmax(score)))

    return new_labels

def preprocess_classification(image, y1, y2, x1, x2): # preprocessing depends on model implementation! (grayscale + equalisation + normalisation)
    global count
    image = image[int(y1):int(y2), int(x1):int(x2)]
    image = Image.fromarray(image)
    image = ImageOps.grayscale(image)
    image = ImageOps.equalize(image, mask = None)
    image = image.resize((32,32))
    image = np.array(image) 
    image = image / 255.0
    image = np.expand_dims(image, axis=0)

    return image

def convert_image(image_bytes):

    #bytes = base64.b64decode(image_bytes)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    return img

if __name__ == "__main__":
    asyncio.run(main())