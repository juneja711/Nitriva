# Nitriva — Python AI/ML Assistive Eye-Gaze & Wink Controlled Interface 👁️💬

> **Empowering non-verbal and paralyzed individuals through accessible, hands-free computer vision built with Python, OpenCV, and MediaPipe.**

**Nitriva** is a Python-powered assistive communication and smart environmental control platform designed for individuals living with motor disabilities, ALS (Amyotrophic Lateral Sclerosis), quadriplegia, cerebral palsy, or locked-in syndrome.

The core AI/ML engine runs entirely in **Python**, utilizing **OpenCV** and **Google MediaPipe Tasks Vision (FaceLandmarker with 478 3D facial landmarks and 52 Blendshapes)** to translate subtle eye gaze, left-eye winks, and dual blinks into expressive communication, smart home interactions, and emergency caregiver alerts.

---

## 🌟 Core AI / ML Architecture (Python)

1. **`optics_engine.py` (Computer Vision Engine)**:
   - **Landmark Estimation**: Uses MediaPipe Tasks Vision (`FaceLandmarker`) with `face_landmarker.task` for 478 3D landmarks + iris localization.
   - **Eye Aspect Ratio (EAR)**: Computes Euclidean geometric eyelid distances to track blinks and winks in real time.
   - **Gesture Classification**:
     - **Left Wink**: Isolated left eyelid closure ($EAR_{left} < 0.20$, $EAR_{right} > 0.27$) triggers `LEFT WINK (SELECTING)` to select cards.
     - **2 Blinks**: Both eyes blink twice within 2.5s -> `2 BLINKS (BACK)` to return to Dashboard.
     - **3 Blinks**: Both eyes blink thrice within 2.5s -> `3 BLINKS (DISCONNECT)` to log out.
   - **Iris Gaze Vector**: Calculates horizontal and vertical displacement of the pupil center within the eye corners.
   - **Dual-Phase Affine Calibration**: Computes an affine transformation matrix mapping raw iris coordinates to screen coordinates.

2. **`sentence_generator.py` (Natural Language AI Synthesizer)**:
   - Contextual rule engine and NLP matrix converting selected AAC keywords (e.g., `["water", "hungry"]`) into fluent conversational sentences:
     *"I am feeling hungry and thirsty, can I get some food and water?"*

3. **`tts_engine.py` (Voice Audio Engine)**:
   - Real-time text-to-speech engine using native Windows SAPI speech synthesis in non-blocking daemon threads.

4. **`app.py` (Flask Server & Live Telemetry API)**:
   - Streams live annotated OpenCV frames (`/video_feed`) showing eye bounding lines, iris centers, gaze vector arrows, and HUD status.
   - Exposes REST telemetry endpoints (`/api/telemetry`, `/api/synthesize`, `/api/toggle_device`, `/api/login`).

5. **`desktop_gui.py` (Native Python OpenCV Desktop App)**:
   - Standalone desktop application with an interactive visual Heads-Up Display (HUD) powered by OpenCV.

---

## 🚀 How to Run

### Mode 1: Python Web Application (Flask + OpenCV)
```powershell
python app.py
```
Open your browser to: **[http://localhost:5000](http://localhost:5000)**
- Patient Access Key: `1234`
- Live computer vision video feed streamed from OpenCV via `/video_feed`!

### Mode 2: Native Python OpenCV Desktop HUD
```powershell
python desktop_gui.py
```
- Launches a native OpenCV desktop window with real-time interactive quadrants, iris tracking, and voice synthesis!
- Look at a card and **wink your left eye** to select it.
- **Blink twice** to go back.
- Press **`q`** to exit.

---

## 📦 Requirements & Installation

```bash
pip install -r requirements.txt
```

Packages used:
- `opencv-python>=4.9.0`
- `mediapipe>=0.10.0`
- `numpy>=1.24.0`
- `flask>=3.0.0`
- `flask-cors>=4.0.0`

---

## 📁 Repository Structure

```
nitriva/
├── optics_engine.py       # Core Python AI/ML computer vision & gesture engine
├── sentence_generator.py  # Natural language contextual sentence synthesizer
├── tts_engine.py          # Python text-to-speech synthesizer
├── app.py                 # Flask server with live OpenCV MJPEG video streaming
├── desktop_gui.py         # Standalone native OpenCV desktop HUD application
├── face_landmarker.task   # MediaPipe FaceLandmarker model weights
├── requirements.txt       # Python package dependencies
├── server.py              # Lightweight static fallback server
├── index.html             # UI shell
├── assets/                # UI styling and client assets
└── vercel.json            # Cloud deployment configuration
```

---

## 🔒 Privacy & Security

All facial and iris landmark processing is computed **100% locally on-device** using your machine's CPU/GPU. No video frames, biometric telemetry, or user data are ever uploaded or transmitted externally.
