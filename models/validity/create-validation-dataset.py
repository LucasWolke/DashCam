import csv

traffic_signs = [
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

never_valid = [6, 32, 41, 42]

# sign2 replaces sign1 -> 0
# both signs valid -> 1
# no signs valid -> 2
# only first sign valid -> 3

# WIP: might not be 100% accurate for now - good enough for testing model accuracy
# class 1: 0-8 (without 6) -> Replaced by each other, 32 and 5 by 6
# class 2: 9-10 -> Ended by 32, 41/42
# class 3: 12 -> Ended by 13,14
# class 4: 11-40 (not 12) -> only while in vision

import itertools

traffic_sign_ids = [0, 1, 2, ..., 42]

# Generate all possible pairs of traffic signs

pairs = list(itertools.combinations(traffic_sign_ids, 2))

training_data = []


def checkIfOnlyFirst(sign1, sign2):
    if sign2 == 6:
        if sign1 <= 12 and sign1 != 5 and sign1 != 11:
            return True
    if sign2 == 32:
        if sign1 == 12:
            return True
    if sign2 == 41 or sign2 == 42:
        if sign1 <= 8 and sign1 == 12:
            return True
    return False

def checkIfSame(sign1, sign2):
    return sign1 == sign2

# The following functions need more comments / cleaner and less error-prone implementation 
def checkIfReplaces(sign1, sign2):
    if(sign1 >= 0 and sign1 <= 8):
        if(sign2 >= 0 and sign2 <= 8):
            return True
    if(sign1 >= 11 and sign1 <= 40 and sign1 != 12):
        if(sign2 not in never_valid):
            return True
    return False

def checkIfEnds(sign1, sign2):
    if(sign1 == 5 and sign2 == 6):
        return True
    if(sign1 >= 0 and sign1 <= 8 and sign2 == 32):
        return True
    if(sign1 == 9 and (sign2 == 32 or sign2 == 41)):
        return True
    if(sign1 == 10 and (sign2 == 32 or sign2 == 42)):
        return True
    if(sign1 == 12 and (sign2 == 13 or sign2 == 14)):
        return True
    if(sign1 >= 11 and sign1 <= 40 and sign1 != 12):
        if(sign2 in never_valid):
            return True
    return False

label2_augmentation = []

for x in range(0,43):
    for y in range(0,43):
        if(x in never_valid): # these signs can never be active so we skip them
            continue
        label = 0
        if (checkIfOnlyFirst(x, y)):
            label = 3
        elif (checkIfSame(x, y)):
            label = 1
        elif (checkIfReplaces(x,y)):
            label = 0
        elif (checkIfEnds(x,y)):
            label = 2
            label2_augmentation.append([x, y, label])
        else:
            label = 1

        training_data.append([x, y, label])

# data if there is no second sign
for y in range(0, 10):
    for x in range(0,42):
        if x in never_valid:
            continue
        if(x >= 13 and x <= 40):
            training_data.append([x, 43, 2])
        else:
            for j in range(0,5):
                training_data.append([x, 43, 3])

# data if there is no first sign
for y in range(0, 10):
    for x in range(0,42):
        if x in never_valid:
            for j in range(0,5):
                training_data.append([43, x, 2])
        else:
                training_data.append([43, x, 0])

# since there are ~10 times less label 2 we manually add the data in 10 times more often to balance out the dataset
for x in range(0, 10):
    for y in range(0, len(label2_augmentation)):
        training_data.append(label2_augmentation[y])

# Save the training data to a CSV file
with open('traffic_signs.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(training_data)