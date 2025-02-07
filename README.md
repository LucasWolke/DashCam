# 🚦DashCam App

**DashCam App** is an full-stack application that detects and classifies traffic signs in real-time using multiple deep learning models.

![App Preview](https://i.imgur.com/8I41dmz.png)


## Features
 -  **Traffic Sign Detection** - Real-time detection of traffic signs using YOLOv8
 -  **Sign Classification** - Accurate classification of detected signs into specific categories using ResNet50  
 -  **Active Sign Validation** - Validates which traffic signs are currently active
 -  **Real-time Processing** - Real time video feed with detected and currently active traffic signs in Android App

## Tech Stack

- ![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)
- ![Java](https://img.shields.io/badge/Java-%23ED8B00.svg?logo=openjdk&logoColor=white)
- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
- ![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
- ![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=socket.io&logoColor=white)

## Workflow

The application workflow consists of two main components, illustrated below: The frontend flow handles camera access, video streaming, and visualization, while the backend manages the computer vision pipeline including detection, classification and validation of traffic signs. Both components communicate via WebSocket, ensuring real-time processing and feedback.

![Frontend Workflow](https://i.imgur.com/9mWTRTM.png)

![Backend Workflow](https://i.imgur.com/ecQpzZM.png)

## Usage

### Backend Setup

1. Clone the repository:
	```bash
	git clone https://github.com/LucasWolke/DashCam.git
	```

2. Navigate to backend directory:

	```bash
	cd DashCam/backend
	```

3. Install dependencies:
	```bash
	pip install -r requirements.txt
	```

4. Start the WebSocket server:

	```bash
	python websocket.py
	```
5.  After succesfully starting websocket, enter IPv4 Address (can be found with "ipconfig" in terminal)

### Frontend Setup

1. Install Android Studio
2. Open the "frontend" folder in Android Studio
3. Connect your Android device via USB (enable USB Debugging)
4. Click "run 'app'" to start application on the phone
5. Enter the same IPv4 Address used in the backend setup
