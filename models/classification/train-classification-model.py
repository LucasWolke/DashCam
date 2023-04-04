import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import tensorflow as tf
from sklearn.model_selection import train_test_split

from tensorflow import keras

batch_size = 32
img_height = 32
img_width = 32

num_classes = 43
img_array = []
labels = []

# iterate over all images in the 43 image folders
for i in range(num_classes): 
  path = '../../datasets/classification/GTSRB/Train/'+ str(i)
  images = os.listdir(path) 
  for img_name in images:
    try:
      # open, preprocess, normalize - add further preprocessing later!
      img = Image.open(path + '/' + img_name)
      img = ImageOps.grayscale(img)
      img = img.resize((32,32))
      img = np.array(img) 
      img = img / 255.0
      img_array.append(img) 
      labels.append(i)
    except:
      print('error opening image ' + img_name)

img_array = np.array(img_array)
labels = np.array(labels)

# 80 20 training - validation split
train_ds, val_ds, train_labels, val_labels = train_test_split(img_array, labels, test_size=0.2, random_state=69)

# very simple CNN for testing purposes
model = tf.keras.Sequential([
  tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(32, 32, 1)),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dense(num_classes)
])

model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['SparseCategoricalAccuracy'])

epochs=15

model.fit(train_ds, train_labels, batch_size=batch_size, epochs=epochs, validation_data=(val_ds, val_labels))

model.summary()

model.save('./simple-classification-model/') 

# ~99.64% accuracy on training data
# ~99.18% acc on validation data
# ~~95% acc on test data -> overfitting. More sophisticated model will include dropout layers

