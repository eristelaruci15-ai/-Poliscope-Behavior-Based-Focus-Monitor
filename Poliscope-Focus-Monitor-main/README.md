# Poliscope – Behavior-Based Focus Monitor

Poliscope is a real-time AI self-study assistant built using computer vision. 
The system monitors user focus through face detection, head pose estimation, and gaze tracking.

It helps students improve concentration by detecting whether they are engaged, distracted, or absent during study sessions.


## Features

- Real-time face detection using webcam
- Head pose tracking 
- Eye position and gaze estimation
- Personalized calibration system
- Behavior classification (Engaged / Distracted / Absent)
- Visual assistant feedback
- Modular and structured code design


## How It Works

- The webcam captures live video input
- MediaPipe detects facial landmarks
- Head and eye positions are calculated
- The system compares current position to a calibrated baseline
- Focus state is classified in real time


## Technologies Used

- Python
- OpenCV
- MediaPipe
- NumPy
- Real-time video processing


## Installation

1. Create a virtual environment

python -m venv venv

2. Activate the virtual environment (Windows)

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Run the project

python main.py


## Academic Purpose

This project was developed as an AI-based behavioral monitoring system to support self-study improvement.

It demonstrates real-time computer vision, behavioral analysis, and personalized AI calibration.


## Team

- @iisra0180-max
- @martinakoci13-arch
- @eristelaruci15-ai
- @Patrikgit-hub



