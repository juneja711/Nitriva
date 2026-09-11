import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time
import math
import os

class NitrivaOpticsEngine:
    """
    Production AI/ML Computer Vision Engine for Nitriva in Python.
    Uses MediaPipe Tasks FaceLandmarker with 478 3D landmarks + 52 Blendshapes,
    OpenCV frame processing, iris tracking, EAR calculations, and wink/blink detection.
    """
    def __init__(self, camera_index=0, model_path=None):
        self.camera_index = camera_index
        self.cap = None

        if model_path is None:
            dir_path = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(dir_path, "face_landmarker.task")

        # Initialize MediaPipe Tasks FaceLandmarker
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=1
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

        # Gaze smoothing and calibration
        self.raw_x = 0.5
        self.raw_y = 0.5
        self.screen_x = 0.5
        self.screen_y = 0.5
        self.affine = {"mx": 1.0, "bx": 0.0, "my": 1.0, "by": 0.0}

        # Gesture recognition & debouncing
        self.ear_left = 0.3
        self.ear_right = 0.3
        self.blink_left = 0.0
        self.blink_right = 0.0
        self.blink_history = []
        self.was_blinking = False
        self.active_gesture = "TRACKING GAZE..."
        self.face_detected = False
        self.last_action_time = 0
        self.active_card = 0

        # Calibration state
        self.calib_phase = "DONE"
        self.calib_step = 0
        self.calib_samples = []
        self.is_collecting = False
        self.simulation_mode = False

    def start_camera(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def stop_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def process_frame(self, frame=None):
        if frame is None:
            if self.cap is None or not self.cap.isOpened():
                self.start_camera()
            ret, frame = self.cap.read()
            if not ret or frame is None:
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank, "CAMERA ACTIVE - LOOK HERE", (140, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 128), 2)
                return blank, self.get_telemetry()

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        res = self.landmarker.detect(mp_img)

        now = time.time()
        gesture_detected = None

        if res.face_landmarks and len(res.face_landmarks) > 0:
            self.face_detected = True
            lm = res.face_landmarks[0]

            # Blendshapes for eye blinks
            if res.face_blendshapes and len(res.face_blendshapes) > 0:
                bs_map = {b.category_name: b.score for b in res.face_blendshapes[0]}
                self.blink_left = bs_map.get("eyeBlinkLeft", 0.0)
                self.blink_right = bs_map.get("eyeBlinkRight", 0.0)

            # Iris landmarks: 468 (right iris center), 473 (left iris center)
            # Eye bounding landmarks:
            # Right eye: 33 (outer), 133 (inner), 159 (upper), 145 (lower)
            # Left eye: 362 (inner), 263 (outer), 386 (upper), 374 (lower)
            r_iris = (int(lm[468].x * w), int(lm[468].y * h))
            l_iris = (int(lm[473].x * w), int(lm[473].y * h))
            r_out = (int(lm[33].x * w), int(lm[33].y * h))
            r_in = (int(lm[133].x * w), int(lm[133].y * h))
            l_in = (int(lm[362].x * w), int(lm[362].y * h))
            l_out = (int(lm[263].x * w), int(lm[263].y * h))

            r_width = max(1, abs(r_in[0] - r_out[0]))
            l_width = max(1, abs(l_out[0] - l_in[0]))
            norm_x = (((r_iris[0] - r_out[0]) / r_width) + ((l_iris[0] - l_in[0]) / l_width)) / 2.0

            r_h = max(1, abs(int(lm[145].y * h) - int(lm[159].y * h)))
            l_h = max(1, abs(int(lm[374].y * h) - int(lm[386].y * h)))
            norm_y = (((r_iris[1] - int(lm[159].y * h)) / r_h) + ((l_iris[1] - int(lm[386].y * h)) / l_h)) / 2.0

            # Smoothing
            self.raw_x = norm_x * 0.6 + self.raw_x * 0.4
            self.raw_y = norm_y * 0.6 + self.raw_y * 0.4

            # Affine calibration
            sx = self.raw_x * self.affine["mx"] + self.affine["bx"]
            sy = self.raw_y * self.affine["my"] + self.affine["by"]
            sx = (sx - 0.5) * 1.3 + 0.5
            sy = (sy - 0.5) * 1.3 + 0.5
            self.screen_x = max(0.0, min(1.0, sx))
            self.screen_y = max(0.0, min(1.0, sy))

            # Gesture detection
            is_left_wink = (self.blink_left > 0.35 and (self.blink_left - self.blink_right) > 0.15)
            is_both_blinking = (self.blink_left > 0.45 and self.blink_right > 0.45 and not is_left_wink)

            if is_left_wink and not is_both_blinking:
                if now - self.last_action_time > 1.2:
                    self.active_gesture = "LEFT WINK (SELECTING)"
                    self.last_action_time = now
                    gesture_detected = "WINK"
            elif now - self.last_action_time > 1.0:
                self.active_gesture = "TRACKING GAZE..."

            # Multi-blink counting
            if is_both_blinking and not self.was_blinking:
                self.blink_history.append(now)
                self.was_blinking = True
            elif not is_both_blinking:
                self.was_blinking = False

            self.blink_history = [t for t in self.blink_history if now - t < 2.5]

            if len(self.blink_history) >= 3:
                self.active_gesture = "3 BLINKS (DISCONNECT)"
                self.last_action_time = now + 1.5
                self.blink_history = []
                gesture_detected = "DISCONNECT"
            elif len(self.blink_history) == 2 and (now - self.blink_history[1] > 0.35) and not is_both_blinking:
                self.active_gesture = "2 BLINKS (BACK)"
                self.last_action_time = now + 1.5
                self.blink_history = []
                gesture_detected = "BACK"

            # Annotate OpenCV frame
            cv2.circle(frame, r_iris, 4, (0, 255, 128), -1)
            cv2.circle(frame, l_iris, 4, (0, 255, 128), -1)
            cv2.line(frame, r_out, r_in, (255, 200, 0), 1)
            cv2.line(frame, l_in, l_out, (255, 200, 0), 1)

            # Gaze vector from forehead (landmark 10)
            fh = (int(lm[10].x * w), int(lm[10].y * h))
            dx = int((self.screen_x - 0.5) * 80)
            dy = int((self.screen_y - 0.5) * 80)
            cv2.arrowedLine(frame, fh, (fh[0] + dx, fh[1] + dy), (0, 255, 255), 2, tipLength=0.3)

            # Status bar
            cv2.rectangle(frame, (10, h - 45), (w - 10, h - 10), (15, 23, 42), -1)
            cv2.circle(frame, (25, h - 27), 5, (0, 255, 128), -1)
            cv2.putText(frame, f"{self.active_gesture}  [X:{self.screen_x:.2f} Y:{self.screen_y:.2f}]",
                        (40, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            self.face_detected = False
            self.active_gesture = "FACE LOST"
            cv2.rectangle(frame, (10, h - 45), (w - 10, h - 10), (15, 23, 42), -1)
            cv2.circle(frame, (25, h - 27), 5, (0, 0, 255), -1)
            cv2.putText(frame, "FACE LOST - Center face in frame", (40, h - 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 150, 255), 1)

        telemetry = self.get_telemetry()
        telemetry["gesture_event"] = gesture_detected
        return frame, telemetry

    def get_telemetry(self):
        return {
            "screen_x": round(float(self.screen_x), 3),
            "screen_y": round(float(self.screen_y), 3),
            "blink_left": round(float(self.blink_left), 3),
            "blink_right": round(float(self.blink_right), 3),
            "active_gesture": self.active_gesture,
            "face_detected": self.face_detected,
            "calib_phase": self.calib_phase,
            "calib_step": self.calib_step,
            "simulation_mode": self.simulation_mode
        }
