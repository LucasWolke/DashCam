import numpy as np
import os
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
from csv import reader

model = tf.keras.models.load_model('./simple-classification-model')

correct_labels = []

# read in correct labels from csv file and store them in an array 
with open('../../datasets/classification/GTSRB/Test.csv', 'r') as read_file:
    csv_reader = reader(read_file)
    for row in csv_reader:
        correct_labels.append(row[6])

count = 1;
correct = 0;

path = '../../datasets/classification/GTSRB/Test'
images = os.listdir(path) 
for a in images: # IMPORTANT! Use same preprocessing as in model training
    image = Image.open(path + '/' + a)
    image = ImageOps.grayscale(image)
    image = image.resize((32,32))
    image = np.array(image) 
    image = image / 255.0
    img_array = [tf.expand_dims(image, 0)]
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    if int(np.argmax(score)) == int(correct_labels[count]):
        correct+=1;
    count+=1;

print('Total: ' + str(count) + ', Correct: ' + str(correct))