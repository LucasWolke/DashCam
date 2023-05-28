import numpy as np
import os
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
from csv import reader
import time

model = tf.keras.models.load_model('./classification-model-augmented', compile=False)
model.compile()

correct_labels = []

# read in correct labels from csv file and store them in an array 
with open('../../datasets/classification/GTSRB/Test.csv', 'r') as read_file:
    csv_reader = reader(read_file)
    for row in csv_reader:
        correct_labels.append(row[6])

count = 0;
stackCount = 0;
correct = 0;
skip = 0
imageStack = []

start_time = time.time()

path = '../../datasets/classification/GTSRB/Test'
images = os.listdir(path) 
for a in images: # IMPORTANT! Use same preprocessing as in model training
    image = Image.open(path + '/' + a)
    image = ImageOps.grayscale(image)
    image = ImageOps.equalize(image, mask = None)
    image = image.resize((32,32))
    image = np.array(image) 
    image = image / 255.0
    img_array = tf.expand_dims(image, axis=0)
    imageStack.append(img_array)
    stackCount+=1
    if(stackCount%32 == 0):
        predictions = model.predict(np.vstack(imageStack))
        imageStack = []
        for prediction in predictions:
            count+=1
            score = tf.nn.softmax(prediction)
            max_prob = np.max(score.numpy())
            if max_prob < 0.99: # when the model is not more than 75% sure about its prediction we disregard its prediction (might need to tweak the amount!)
                skip+=1
            elif int(np.argmax(score)) == int(correct_labels[count]):
                correct+=1

print('Total: ' + str(count) + ', Correct: ' + str(correct) + ', Skip: ' + str(skip))

end_time = time.time()
execution_time = end_time - start_time

print(f"Execution time: {execution_time} seconds")