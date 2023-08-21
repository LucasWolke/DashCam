from ipaddress import ip_address
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

print("Loading deep learning models...")

model_classification = tf.keras.models.load_model('../models/classification/col-50-augmented-autocontrast-best', compile=False)
model_classification.compile()

model_validity = tf.keras.models.load_model('../models/validity/validity-model-checkpoint', compile=False)
model_validity.compile()

model_detection = YOLO("../models/detection/runs/detect/train8/weights/best.pt") #import yolov8 detection model

print("Models loaded succesfully.")
print("Enter the IP address where the WebSocket should be hosted:")
ip_address = input()

valid_labels = []

detection_results = []

timeStart = 0

async def handler(websocket):
    while True:
            global timeStart
            global valid_labels
            global new_labels
            image = await websocket.recv()
            timeStart = time.time()
            image = convert_image(image)
            response = await detection(image, websocket)
            response = (json.dumps(response))
            await websocket.send(response)
            new_labels = []
            end = time.time()
            print("Total time:" + str(end - timeStart))

async def main():
    async with websockets.serve(handler, ip_address, 8001): # insert ipv4 address here
        print("WebSocket created on ip " + ip_address + ":8001")
        print("Enter this ip in the app to start detections!")
        await asyncio.Future()

async def detection(image, websocket):
    global valid_labels
    # disregard predictions with >50% confidence
    results = model_detection(image, conf=0.5)
    rois = []
    ret_arr = []
    for result in results:
        boxes = result.boxes
        # get the vertices of the bounding box
        for box in boxes:
            x1 = box.xyxy.cpu().numpy()[0][0]
            y1 = box.xyxy.cpu().numpy()[0][1]

            x2 = box.xyxy.cpu().numpy()[0][2]
            y2 = box.xyxy.cpu().numpy()[0][3]
            
            ret_str = str(x1) + "," + str(y1) +","+ str(x2) +","+ str(y2)
            ret_arr.append(ret_str)

            # preprocessing before classification
            rois.append(preprocess_classification(image, y1, y2, x1, x2))

        # send the bounding boxes back right away for lower latency
        response = (json.dumps([ret_arr, valid_labels]))

        await websocket.send(response)

        # classification + validation
        new_labels = classification(rois)
        
        valid_labels = validation(list(set(new_labels)))

        return ([ret_arr, valid_labels])

def validation(new_labels):
    print(new_labels)
    global valid_labels
    # 43 added when no new labels, stands for "no" sign
    if len(new_labels) == 0:
        new_labels.append(43)
    if len(valid_labels) == 0:
        valid_labels.append(43)
    label_combinations = []
    # create all label combinations of sign1's and sign2's
    for x in valid_labels:
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

# preprocessing depends on model implementation!
def preprocess_classification(image, y1, y2, x1, x2):

    # make bounding boxes less tight by adding 5px padding
    x1 = max(0, int(x1) - 5)
    y1 = max(0, int(y1) - 5)
    x2 = min(image.shape[1], int(x2) + 5)
    y2 = min(image.shape[0], int(y2) + 5) 

    # autocontrast, resizing, normalisation
    # cut ROIs out
    image = image[y1:y2, x1:x2]
    image = Image.fromarray(image)
    image = ImageOps.autocontrast(image)
    image = image.resize((32,32))
    image = np.array(image) 
    image = image / 255.0
    image = np.expand_dims(image, axis=0)

    return image

def classification(images):

    new_labels = []
    if(len(images) == 0):
        return new_labels
    
    with tf.device("gpu:0"):
        # vstack creates a batch
        predictions = model_classification.predict(np.vstack(images))
    for prediction in predictions:
        # get probability distribution
        score = tf.nn.softmax(prediction)
        # get probability of highest score
        max_prob = np.max(score.numpy())
        # predictions with a confidence below 75% are disregarded
        if max_prob < 0.75:
            continue
        # highest score is the predicted sign
        new_labels.append(int(np.argmax(score)))

    return new_labels

def convert_image(image_bytes):
    # byte array to np array
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    # convert array to image
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    # cv2 images are BGR per default, convert to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

if __name__ == "__main__":
    asyncio.run(main())