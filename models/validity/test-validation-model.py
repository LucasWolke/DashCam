import numpy as np
import os
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf

import csv
from csv import reader

model = tf.keras.models.load_model('./validity-model-checkpoint')

# read in correct labels from csv file and store them in an array 

total = 0
correct = 0

wrong = []

with open('traffic_signs.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    # iterave over entire training data
    for row in reader:
        total += 1
        test = (int(row[0]),int(row[1]))
        arr = [tf.expand_dims(test, 0)]
        predictions = model.predict(arr)
        # gets actual label from model prediction and compares it to correct label 
        if(str(np.argmax(tf.nn.softmax(predictions[0]))) == str(row[2])):
            correct += 1
        else:
            # save wrong inputs to learn where shortcomings of model lie
            wrong.append((int(row[0]),int(row[1])))
        if total % 500 == 0:
            print(total)
        if total >= 6000:
            break
print(total)
print(correct)
print(correct/total)
print(wrong)