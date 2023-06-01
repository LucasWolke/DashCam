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
labelStack = []
stackCount = 0
rows = []

with open('traffic_signs.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    # iterave over entire training data
    for row in reader:
        rows.append(row)
        tuple = (int(row[0]),int(row[1]))
        arr = tf.expand_dims(tuple, 0)
        labelStack.append(arr)
        stackCount+=1
        if(stackCount%32 == 0):
            predictions = model.predict(np.vstack(labelStack))
            labelStack = []
            for prediction in predictions:
                score = tf.nn.softmax(prediction)
                max_prob = np.max(score.numpy())
                if(str(np.argmax(score)) == str(rows[total][2])):
                    correct += 1
                # gets actual label from model prediction and compares it to correct label 
                else:
                    # save wrong inputs to learn where shortcomings of model lie
                    wrong.append((int(rows[total][0]),int(rows[total][1])))
                total+=1
print(total)
print(correct)
print(correct/total)
print(wrong)