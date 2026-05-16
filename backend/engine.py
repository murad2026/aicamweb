import cv2
import time
import threading
import requests
from ultralytics import YOLO

model = None

def get_model():
    global model
    if model is None:
        model = YOLO("/Users/Apple/ai-security/yolov8s.pt")
    return model

CLASS_NAMES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle",
    5: "bus", 7: "truck", 15: "cat", 16: "dog"
}

TELEGRAM_TOKEN = "8575525286:AAGUkWh-ro35d8Pru6tODRv8sw4Ingv35nM"

def send_telegram(chat_id, frame, caption):
    _, buf = cv2.imencode('.jpg', frame)
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": ("snap.jpg", buf.tobytes(), "image/jpeg")}
        )
        print(f"✅ Telegram -> {chat_id}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def resolve_chat_id(username):
    username = username.replace("@", "")
    r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates")
    data = r.json()
    for update in data.get("result", []):
        chat = update.get("message", {}).get("chat", {})
        if chat.get("username", "").lower() == username.lower():
            return str(chat["id"])
    return None

def in_zone(p, zone, frame_w, frame_h, grid_cols=16, grid_rows=9):
    if not zone or not zone.get("cells"):
        return True  # если зона не настроена — алертим везде
    cx = (p["x"] + p["w"] // 2) / frame_w
    cy = (p["y"] + p["h"] // 2) / frame_h
    col = int(cx * grid_cols)
    row = int(cy * grid_rows)
    return [row, col] in zone["cells"]

def detect_frame(frame, detect_classes, conf=0.5):
    m = get_model()
    results = m(frame, verbose=False)[0]
    detections = []
    for box in results.boxes:
        cls = int(box.cls[0])
        confidence = float(box.conf[0])
        cls_name = CLASS_NAMES.get(cls)
        if cls_name and cls_name in detect_classes and confidence >= conf:
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            detections.append({"class": cls_name, "conf": confidence, "x": x1, "y": y1, "w": x2-x1, "h": y2-y1})
    return detections

class CameraWorker:
    def __init__(self, camera):
        self.camera = camera
        self.running = False
        self.thread = None
        self.present = False
        self.last_alert = 0
        self.alert_count = 0
        self.COOLDOWN = 60
        self.MAX_ALERTS = 1
        self.last_seen = 0
        self.EXIT_DELAY = 10

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(f"🎥 Started: {self.camera['name']}")

    def stop(self):
        self.running = False

    def _loop(self):
        cap = cv2.VideoCapture(self.camera["rtsp_url"])
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        while self.running:
            ret, frame = cap.read()
            if not ret:
                print(f"🔄 Reconnecting: {self.camera['name']}")
                cap.release()
                time.sleep(3)
                cap = cv2.VideoCapture(self.camera["rtsp_url"])
                continue

            h, w = frame.shape[:2]
            detections = detect_frame(frame, self.camera.get("detect_classes", ["person"]))
            in_zone_det = [d for d in detections if in_zone(d, self.camera.get("zone"), w, h)]
            now = time.time()

            if in_zone_det and not self.present:
                self.present = True
                self.alert_count = 0

            if in_zone_det and self.present:
                if now - self.last_alert > self.COOLDOWN and self.alert_count < self.MAX_ALERTS:
                    self.last_alert = now
                    self.alert_count += 1
                    cls_names = list(set(d["class"] for d in in_zone_det))
                    caption = f"🚨 {self.camera['name']}: {', '.join(cls_names)} detected"
                    print(f"🔴 {caption}")
                    # сохраняем событие
                    try:
                        from database import SessionLocal, EventDB
                        from datetime import datetime
                        db = SessionLocal()
                        event = EventDB(
                            camera_id=self.camera["id"],
                            camera_name=self.camera["name"],
                            detected=", ".join(set(d["class"] for d in in_zone_det)),
                            confidence=f"{max(d['conf'] for d in in_zone_det):.2f}",
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        db.add(event)
                        db.commit()
                        db.close()
                    except Exception as e:
                        print(f"❌ Event save error: {e}")
                    if self.camera.get("notify_telegram"):
                        chat_id = resolve_chat_id(self.camera["notify_telegram"])
                        if chat_id:
                            send_telegram(chat_id, frame, caption)

            elif not in_zone_det and self.present:
                if now - self.last_seen > self.EXIT_DELAY:
                    self.present = False
                    self.alert_count = 0
                    print(f"✅ Clear: {self.camera['name']}")
            
            if in_zone_det:
                self.last_seen = now

            time.sleep(0.5)
        cap.release()

# --- глобальный менеджер ---
workers = {}

def start_camera(camera):
    cam_id = camera["id"]
    if cam_id in workers:
        workers[cam_id].stop()
    w = CameraWorker(camera)
    w.start()
    workers[cam_id] = w

def stop_camera(cam_id):
    if cam_id in workers:
        workers[cam_id].stop()
        del workers[cam_id]

def get_status():
    return {cam_id: {"name": w.camera["name"], "present": w.present, "running": w.running} for cam_id, w in workers.items()}
