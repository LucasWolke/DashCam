from ultralytics import YOLO

model = YOLO("yolov8s.pt")  # load pretrained yolo

def freeze_support(): # this prevents it from crashing while training
    model.train(data="C:/Users/wolke/OneDrive/Desktop/BachelorArbeit/DashCam/datasets/detection/detection-300/data.yaml", epochs=5, imgsz=640)

if __name__ == '__main__':
    freeze_support()