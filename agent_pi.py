"""
AI Any Camera - Pi Agent (Lite)
For Raspberry Pi Zero W / weak devices
No local YOLO - sends frames to server for detection
"""

import cv2
import time
import base64
import requests
import subprocess
import numpy as np
import os
import json
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
SERVER_URL = os.environ.get("SERVER_URL", "https://aianycamera.com")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")         # User JWT token
CAMERA_ID  = int(os.environ.get("CAMERA_ID", "1"))
RTSP_URL   = os.environ.get("RTSP_URL", "")
FPS        = int(os.environ.get("FPS", "1"))           # 1 FPS default for Pi Zero
JPEG_QUALITY = int(os.environ.get("JPEG_QUALITY", "60"))
# ──────────────────────────────────────────────────────────────────────────────

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def encode_frame(frame):
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    return base64.b64encode(buf.tobytes()).decode()

def send_frame(frame_b64):
    """Send frame to server for detection"""
    try:
        r = requests.post(
            f"{SERVER_URL}/api/agent/frame",
            json={
                "token": AUTH_TOKEN,
                "camera_id": CAMERA_ID,
                "image": frame_b64,
            },
            timeout=10
        )
        return r.json()
    except Exception as e:
        log(f"Send error: {e}")
        return None

def send_snapshot(frame_b64):
    """Send snapshot for zone editor / live view"""
    try:
        requests.post(
            f"{SERVER_URL}/api/agent/snapshot",
            json={
                "token": AUTH_TOKEN,
                "camera_id": CAMERA_ID,
                "image": frame_b64,
            },
            timeout=5
        )
    except:
        pass

def get_camera_config():
    """Fetch zone and detect_classes from server"""
    try:
        r = requests.get(
            f"{SERVER_URL}/cameras/{CAMERA_ID}",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=5
        )
        return r.json()
    except:
        return {}

def open_stream(rtsp_url):
    """Open RTSP via ffmpeg pipe - works on Pi Zero W"""
    return subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-vf", f"fps={FPS},scale=640:360",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",
        "-f", "rawvideo", "-"
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**7)

def main():
    if not AUTH_TOKEN:
        print("ERROR: AUTH_TOKEN not set")
        print("Set it: export AUTH_TOKEN=your_jwt_token")
        return

    if not RTSP_URL:
        print("ERROR: RTSP_URL not set")
        print("Set it: export RTSP_URL=rtsp://user:pass@192.168.1.x/stream")
        return

    log(f"Starting Pi Agent")
    log(f"Server: {SERVER_URL}")
    log(f"Camera ID: {CAMERA_ID}")
    log(f"FPS: {FPS}")

    frame_w, frame_h = 640, 360
    frame_size = frame_w * frame_h * 3

    snapshot_interval = 30  # Send snapshot every 30s for live view
    last_snapshot = 0
    config_interval = 60    # Refresh config every 60s
    last_config = 0
    cam_config = {}

    proc = open_stream(RTSP_URL)
    log("Stream opened, sending frames...")

    frame_count = 0
    errors = 0

    while True:
        raw = proc.stdout.read(frame_size)

        if len(raw) < frame_size:
            errors += 1
            log(f"Stream lost (attempt {errors}), reconnecting in 5s...")
            proc.kill()
            time.sleep(5)
            proc = open_stream(RTSP_URL)
            continue

        errors = 0
        frame = np.frombuffer(raw, np.uint8).reshape((frame_h, frame_w, 3))
        frame_b64 = encode_frame(frame)
        frame_count += 1
        now = time.time()

        # Refresh config periodically
        if now - last_config > config_interval:
            cam_config = get_camera_config()
            last_config = now
            log(f"Config refreshed: zone={'yes' if cam_config.get('zone') else 'no'}")

        # Send snapshot for live view
        if now - last_snapshot > snapshot_interval:
            send_snapshot(frame_b64)
            last_snapshot = now

        # Send frame for detection
        result = send_frame(frame_b64)
        if result and result.get("detected"):
            log(f"Detection: {result['detected']} (conf {result.get('confidence', '?')})")

    proc.kill()

if __name__ == "__main__":
    main()
