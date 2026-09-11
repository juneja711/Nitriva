from flask import Flask, Response, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import cv2
import os
import json
from optics_engine import NitrivaOpticsEngine
from sentence_generator import NitrivaSentenceSynthesizer
from tts_engine import NitrivaVoiceEngine

app = Flask(__name__, template_folder="templates", static_folder=".")
CORS(app)

engine = NitrivaOpticsEngine(camera_index=0)
synthesizer = NitrivaSentenceSynthesizer()
voice = NitrivaVoiceEngine()

# Global state
app_state = {
    "isLoggedIn": True,
    "route": "/dashboard",
    "devices": {"light": False, "ac": False, "tv": False},
    "selectedKeywords": [],
    "lastSentence": "Select keywords to speak...",
    "volume": 80
}

def generate_video_stream():
    """Generates continuous MJPEG stream of annotated OpenCV frames."""
    while True:
        frame, telemetry = engine.process_frame()
        ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

@app.route("/video_feed")
def video_feed():
    """Live OpenCV annotated computer-vision video feed."""
    return Response(generate_video_stream(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/api/telemetry")
def get_telemetry():
    """Real-time AI telemetry: gaze coordinates, EAR, gesture, face detection."""
    telemetry = engine.get_telemetry()
    telemetry["app_state"] = app_state
    return jsonify(telemetry)

@app.route("/api/synthesize", methods=["POST"])
def synthesize():
    """AI natural language contextual sentence generator."""
    data = request.json or {}
    keywords = data.get("keywords", [])
    sentence = synthesizer.generate(keywords)
    app_state["lastSentence"] = sentence
    app_state["selectedKeywords"] = keywords
    voice.speak(sentence)
    return jsonify({"sentence": sentence})

@app.route("/api/speak", methods=["POST"])
def speak_route():
    data = request.json or {}
    text = data.get("text", "")
    voice.speak(text)
    return jsonify({"status": "ok"})

@app.route("/api/toggle_device", methods=["POST"])
def toggle_device():
    data = request.json or {}
    device = data.get("device", "")
    if device in app_state["devices"]:
        app_state["devices"][device] = not app_state["devices"][device]
        status = "on" if app_state["devices"][device] else "off"
        voice.speak(f"Smart {device.upper()} {status}")
    return jsonify(app_state["devices"])

@app.route("/favicon.svg")
def favicon():
    return send_from_directory(".", "favicon.svg")

@app.route("/")
@app.route("/<path:path>")
def serve_index(path=""):
    return render_template("index.html")

if __name__ == "__main__":
    print("=" * 60)
    print(" Nitriva Python AI/ML Core Server")
    print(" Running at: http://localhost:5000")
    print(" OpenCV & MediaPipe Computer Vision: ACTIVE")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
