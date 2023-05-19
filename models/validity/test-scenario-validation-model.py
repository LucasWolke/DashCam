import numpy as np
import os
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf

import csv
from csv import reader

model_validity = tf.keras.models.load_model('./validity-model-checkpoint')

label_guide = [
    "0. Speed limit (20km/h)",
    "1. Speed limit (30km/h)",
    "2. Speed limit (50km/h)",
    "3. Speed limit (60km/h)",
    "4. Speed limit (70km/h)",
    "5. Speed limit (80km/h)",
    "6. End of speed limit (80km/h)",
    "7. Speed limit (100km/h)",
    "8. Speed limit (120km/h)",
    "9. No passing",
    "10. No passing for vehicles over 3.5 metric tons",
    "11. Right-of-way at the next intersection",
    "12. Priority road",
    "13. Yield",
    "14. Stop",
    "15. No vehicles",
    "16. Vehicles over 3.5 metric tons prohibited",
    "17. No entry",
    "18. General caution",
    "19. Dangerous curve to the left",
    "20. Dangerous curve to the right",
    "21. Double curve",
    "22. Bumpy road",
    "23. Slippery road",
    "24. Road narrows on the right",
    "25. Road work",
    "26. Traffic signals",
    "27. Pedestrians",
    "28. Children crossing",
    "29. Bicycles crossing",
    "30. Beware of ice/snow",
    "31. Wild animals crossing",
    "32. End of all speed and passing limits",
    "33. Turn right ahead",
    "34. Turn left ahead",
    "35. Ahead only",
    "36. Go straight or right",
    "37. Go straight or left",
    "38. Keep right",
    "39. Keep left",
    "40. Roundabout mandatory",
    "41. End of no passing",
    "42. End of no passing by vehicles over 3.5 metric tons"
]

def validation(new_labels):
    global valid_labels
    if len(new_labels) == 0: # if there are no new labels we add 43, which stands for no traffic sign
        new_labels.append(43)
    label_combinations = []
    for x in valid_labels: # create all label combinations of sign1's and sign2's
        for y in new_labels:
            input = (int(x),int(y))
            arr = np.expand_dims(input, axis=0)
            label_combinations.append(arr)

    if(len(label_combinations) == 0):
            return []    

    predictions = model_validity.predict(np.vstack(label_combinations))

    processed_predictions = validation_process_prediction(predictions, label_combinations)

    valid_signs = processed_predictions[0] # all valid signs will be added here

    print("ret:",valid_signs)

    return(valid_signs)

def validation_process_prediction(predictions, label_combinations):

    valid_signs = [] # all valid signs will be added here
    remove = [] # all invalid signs
    print(label_combinations)
    for x,prediction in enumerate(predictions):
            score = (np.argmax(tf.nn.softmax(prediction)))
            print(score)
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
        if x in valid_signs and not (x >= 11 and x <= 40 and x != 12): # never remove "only on sight valid" signs - workaround so that validity model is less complex
            valid_signs.remove(x)
    
    return [valid_signs]

valid_labels = [10] # enter currently valid signs here
new_labels = validation([42]) # enter new signs here
print(new_labels) # prints all signs that are now valid