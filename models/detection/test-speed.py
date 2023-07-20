from ultralytics import YOLO
import time

model_detection = YOLO("./runs/detect/train8/weights/best.pt") #import yolov8 detection model

#def freeze_support():
#    metrics = model_detection.val()

#if __name__ == '__main__':
#    freeze_support()

#0.869      0.495 NANO

#0.953      0.613 MEDIUM

start = time.time()

for x in range(0,1000):
    results = model_detection("./bus.jpg", conf=0.75)

end = time.time()
print(end - start)

# nano: 19.12616539001465 # 38ms

# small: 19.546002626419067 # 39ms 

# medium: 21.924017906188965 # 44ms 