import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow import keras

batch_size = 32

# read in the data
# Format: sign1,sign2,label
data = pd.read_csv('traffic_signs.csv')

x = data.iloc[:,0:2].values

y = data.iloc[:,2].values


# 80 20 training - validation split
train_ds, val_ds, train_labels, val_labels = train_test_split(x, y, test_size=0.2, random_state=69)

# simple CNN for testing purposes - might be good enough already
model = tf.keras.Sequential([
  tf.keras.layers.Dense(units=25, activation='relu', input_dim=2),
  tf.keras.layers.Dense(units=25, activation='relu'),
  tf.keras.layers.Dense(units=25, activation='relu'),
  tf.keras.layers.Dense(units=25, activation='relu'),
  tf.keras.layers.Dense(units=3),
])

model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['SparseCategoricalAccuracy'])

epochs=200

model.fit(train_ds, train_labels, batch_size=batch_size, epochs=epochs, validation_data=(val_ds, val_labels), shuffle=True)

model.summary()

model.save('./simple-validity-model/') 

# since training data includes every single possible combination:
# validation + test data accuraccy: ~98.5 - 100%

