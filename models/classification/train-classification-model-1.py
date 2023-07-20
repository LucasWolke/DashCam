from calendar import c
import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import tensorflow as tf
from sklearn.model_selection import train_test_split
import concurrent.futures

import cv2
from tensorflow import keras

batch_size = 32
img_height = 32
img_width = 32

num_classes = 43
img_array = []
labels = []

count=0
img_numbers = []
counter = 0

def process_item(i, path, img_name):
    try:
        global counter
        counter += 1

        image = Image.open(path + '/' + img_name)
        
        image = ImageOps.autocontrast(image)

        # following lines are different preprocessing techniques
        #image = Image.open(path + '/' + img_name)
        #image = ImageOps.grayscale(image)
        #image = ImageOps.equalize(image, mask = None)
        
        #image = cv2.imread(path + '/' + img_name)
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)

        #image[:,:,0] = cv2.equalizeHist(image[:,:,0])
        #image = cv2.cvtColor(image, cv2.COLOR_YUV2RGB)

        #image = Image.fromarray(image)

        image = image.resize((32,32))
        img = np.array(image) 
        img = img / 255.0
        img_array.append(img) 
        labels.append(i)
    except:
        print('error opening image ' + img_name)

# iterate over all images in the 43 image folders
for i in range(num_classes): 
  path = '../../datasets/classification/GTSRB_augmented/Train/'+ str(i)
  images = os.listdir(path)
  print(i) 
  with concurrent.futures.ThreadPoolExecutor() as executor:
    counter = 0
    futures = [executor.submit(process_item, i, path, img_name) for img_name in images]
    concurrent.futures.wait(futures)
    img_numbers.append(counter)

img_array = np.array(img_array)
labels = np.array(labels)

print(img_numbers)

# 80 20 training - validation split
train_ds, val_ds, train_labels, val_labels = train_test_split(img_array, labels, test_size=0.2, random_state=69)

# 1.3m param architecture

model = tf.keras.Sequential([
  tf.keras.layers.Conv2D(32, (3,3), padding='same', activation='relu', input_shape=(32, 32, 3)),
  tf.keras.layers.Conv2D(32, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Dropout(0.15),
  tf.keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'),
  tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Dropout(0.15),
  tf.keras.layers.Conv2D(128, (3,3), padding='same', activation='relu'),
  tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Dropout(0.15),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(1024, activation='relu'),
  tf.keras.layers.Dropout(0.3),
  tf.keras.layers.Dense(512, activation='relu'),
  tf.keras.layers.Dropout(0.3),
  tf.keras.layers.Dense(num_classes)
])

model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['SparseCategoricalAccuracy'])

epochs=50

model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
    "./col-50-augmented-autocontrast-best",
    monitor = "val_loss",
    verbose = 0,
    save_best_only = True,
    save_weights_only = False,
    mode = "auto",
    save_freq="epoch",
    options=None,
    initial_value_threshold=None,
)


model.fit(train_ds, train_labels, batch_size=batch_size, epochs=epochs, validation_data=(val_ds, val_labels), shuffle=True, callbacks=[model_checkpoint])

model.summary()

model.save('./col-50-augmented-autocontrast') 

