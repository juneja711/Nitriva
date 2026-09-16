# Nitriva (Assistive Eye-Tracking & ML Communication System)

**Nitriva** is a Python & Computer Vision Machine Learning assistive communication system inspired by Nayan Vaani. It empowers individuals with severe speech and motor impairments (e.g., ALS, stroke, cerebral palsy, or locked-in syndrome) to communicate, control smart room devices, and summon care assistance using only their eye gaze, blinks, and winks.

---

## 🌟 Key Features

1. **Patient Setup & Live Camera Framing**:
   - Circular webcam viewfinder matching Nayan Vaani's setup screen.
   - Real-time face presence verification.
2. **Interactive 5-Point Gaze Calibration**:
   - 5 target calibration protocol: Center, Look Top-Left (Phase: Light Mode), Look Top-Right, Look Bottom-Left, Look Bottom-Right.
   - Computes an affine/regression mapping from raw eye vectors to screen coordinates.
3. **Optics Sensor Live HUD**:
   - Real-time webcam overlay with facial detection reticles in the bottom-left sidebar.
   - Dynamic status pill: `● TRACKING ACTIVE`, `● 1 BLINK...`, `● 2 BLINKS (BACK)`, `● 3 BLINKS = LOGOUT`, `● WINK LEFT (SELECT)`.
4. **Modules Dashboard**:
   - **Speech Generator**: Opens communication board.
   - **Device Control**: Smart home integration (Lights, Fan, AC, Nurse Bell).
   - **Emergency SOS**: Loud siren & voice alarm for urgent care.
   - **System Prefs**: Sensitivity and calibration management.
5. **Communication Board with AI Contextual Sentence Synthesis**:
   - 8 Action Cards: `Water`, `Pain`, `Washroom`, `Family`, `Hungry`, `Cold`, `Doctor`, `CLEAR / BACK`.
   - Selecting 1 or 2 keywords automatically synthesizes fluent contextual sentences (e.g. `Water` + `Pain` -> *"I am in pain and urgently need a sip of water."*).
   - Speaks sentences aloud using the browser's Web Speech API and audible tone feedback.
6. **Blink & Wink Gesture Navigation**:
   - **Left Wink**: Select / Activate focused card.
   - **Right Wink**: Clear keyword selections.
   - **2 Blinks**: Navigate Back.
   - **3 Blinks**: Trigger Emergency SOS / Logout.
7. **Accessibility Simulation Mode**:
   - Easily testable even without moving your eyes or in low-light:
     - `Space` / `W`: Wink Left (Select)
     - `B`: Single Blink
     - `2`: Double Blink (Back)
     - `3`: Triple Blink (SOS)
     - `Mouse Movement`: Guides gaze cursor

---

## 🚀 How to Run in VS Code

1. Open VS Code.
2. Go to **File -> Open Folder...** and select:
   ```
   C:\Users\vijit juneja\.gemini\antigravity\scratch\nitriva
   ```
3. Press **`F5`** (or go to Run & Debug and click **"Launch Nitriva ML Server"**).
4. The server will start, and your web browser will automatically open to:
   ```
   http://localhost:8000
   ```

---

## 💻 How to Run from Terminal / PowerShell

```bash
cd "C:\Users\vijit juneja\.gemini\antigravity\scratch\nitriva"
python run.py
```

---

## 🔑 Login & Demo Access

- **Patient Access Key**: `1234` (or `demo`, `nitriva`, `admin`)
- Click or Wink to **Login**.

---

## 🧠 ML Model Architecture

- **Detector**: MediaPipe FaceLandmarker (`face_landmarker.task` bundled locally).
- **Landmarks**: 478 3D facial landmarks including iris centers (landmarks 468 & 473).
- **Blendshapes**: Extracts `eyeBlinkLeft`, `eyeBlinkRight`, `eyeLookUp`, `eyeLookDown`, `eyeLookIn`, `eyeLookOut`.
- **Fusion**: Combines iris geometric displacement and blendshape eye vectors for robust gaze coordinates.
- **Filter**: Exponential Moving Average (EMA) with $\alpha = 0.28$ smoothing to eliminate eye jitter.
