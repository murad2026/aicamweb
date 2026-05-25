import os
import cv2
import time
import threading
import requests
import numpy as np
from ultralytics import YOLO

model = None

def get_model():
    global model
    if model is None:
        model = YOLO("yolov8s.pt")
    return model

CLASS_NAMES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle",
    5: "bus", 7: "truck", 15: "cat", 16: "dog"
}

TELEGRAM_TOKEN = "8575525286:AAGUkWh-ro35d8Pru6tODRv8sw4Ingv35nM"

# ─── Embedding (DeepFace) ─────────────────────────────────────────────────────

_deepface_loaded = False

def get_deepface():
    global _deepface_loaded
    if not _deepface_loaded:
        try:
            from deepface import DeepFace as _df
            _deepface_loaded = True
            return _df
        except Exception as e:
            print(f"DeepFace load error: {e}")
            return None
    from deepface import DeepFace as _df
    return _df

def compute_embedding(crop_bgr):
    """Compute face/person embedding using DeepFace (Facenet512 model)."""
    try:
        import tempfile, os
        # Save crop to temp file
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        _, buf = cv2.imencode('.jpg', crop_bgr)
        tmp.write(buf.tobytes())
        tmp.close()
        df = get_deepface()
        if df is None:
            return _fallback_embedding(crop_bgr)
        result = df.represent(
            img_path=tmp.name,
            model_name="Facenet512",
            enforce_detection=False,
            detector_backend="skip"
        )
        os.unlink(tmp.name)
        if result and len(result) > 0:
            emb = result[0]["embedding"]
            vec = np.array(emb, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return vec.tolist()
    except Exception as e:
        print(f"DeepFace embedding error: {e}")
    return _fallback_embedding(crop_bgr)

def _fallback_embedding(crop_bgr):
    """Fallback: color histogram if DeepFace fails."""
    try:
        img = cv2.resize(crop_bgr, (64, 128))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h = cv2.calcHist([hsv], [0], None, [64], [0, 180]).flatten()
        s = cv2.calcHist([hsv], [1], None, [64], [0, 256]).flatten()
        vec = np.concatenate([h, s]).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0: vec = vec / norm
        return vec.tolist()
    except:
        return None

def cosine_similarity(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    dot = np.dot(a, b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(dot / (na * nb))

SIMILARITY_THRESHOLD = 0.92  # higher threshold for DeepFace embeddings

# ─── DB migration ─────────────────────────────────────────────────────────────

def ensure_db_schema():
    """Add embedding column and subject_sightings table if not exist."""
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    # Add embedding column to subjects
    cols = [r[1] for r in conn.execute("PRAGMA table_info(subjects)").fetchall()]
    if "embedding" not in cols:
        conn.execute("ALTER TABLE subjects ADD COLUMN embedding TEXT")
        print("✅ Added embedding column to subjects")
    if "seen_count" not in cols:
        conn.execute("ALTER TABLE subjects ADD COLUMN seen_count INTEGER DEFAULT 1")
        print("✅ Added seen_count column to subjects")
    if "viewed" not in cols:
        conn.execute("ALTER TABLE subjects ADD COLUMN viewed INTEGER DEFAULT 0")
        print("✅ Added viewed column to subjects")
    # Create subject_sightings table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subject_sightings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            camera_id INTEGER,
            camera_name TEXT,
            timestamp TEXT,
            photo_url TEXT
        )
    """)
    print("✅ subject_sightings table ready")
    conn.commit()
    conn.close()

# ─── Subject matching ─────────────────────────────────────────────────────────

def find_or_create_subject(conn, user_id, camera_id, camera_name, cls, crop_bgr, photo_url, now_str):
    """
    Compare crop embedding against existing subjects for this user+class.
    Returns (subject_id, is_new, is_recurring)
    """
    import json

    embedding = compute_embedding(crop_bgr)

    # Load existing subjects for this user+class that have embeddings
    rows = conn.execute(
        "SELECT id, name, embedding, seen_count FROM subjects WHERE user_id=? AND class=? AND embedding IS NOT NULL",
        (user_id, cls)
    ).fetchall()

    best_id = None
    best_sim = 0.0

    if embedding:
        for row in rows:
            subj_id, name, emb_json, seen_count = row
            if not emb_json:
                continue
            try:
                stored_emb = json.loads(emb_json)
                sim = cosine_similarity(embedding, stored_emb)
                if sim > best_sim:
                    best_sim = sim
                    best_id = subj_id
            except Exception as e:
                print(f"Embedding compare error: {e}")

    if best_id and best_sim >= SIMILARITY_THRESHOLD:
        # Known subject — update
        conn.execute(
            "UPDATE subjects SET seen_count = seen_count + 1, last_seen=?, photo_url=?, viewed=0 WHERE id=?",
            (now_str, photo_url, best_id)
        )
        # Add sighting record
        conn.execute(
            "INSERT INTO subject_sightings (subject_id, camera_id, camera_name, timestamp, photo_url) VALUES (?,?,?,?,?)",
            (best_id, camera_id, camera_name, now_str, photo_url)
        )
        seen_count = conn.execute("SELECT seen_count FROM subjects WHERE id=?", (best_id,)).fetchone()[0]
        print(f"👤 Known subject #{best_id} seen again (sim={best_sim:.2f}, count={seen_count})")
        return best_id, False, True
    else:
        # New subject
        # Count unknowns for naming
        n = conn.execute("SELECT COUNT(*) FROM subjects WHERE user_id=? AND name LIKE 'Unknown%'", (user_id,)).fetchone()[0]
        name = f"Unknown {n + 1}"
        emb_json = json.dumps(embedding) if embedding else None
        conn.execute(
            "INSERT INTO subjects (user_id, camera_id, class, photo_url, first_seen, last_seen, seen_count, viewed, embedding, name) VALUES (?,?,?,?,?,?,1,0,?,?)",
            (user_id, camera_id, cls, photo_url, now_str, now_str, emb_json, name)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # First sighting
        conn.execute(
            "INSERT INTO subject_sightings (subject_id, camera_id, camera_name, timestamp, photo_url) VALUES (?,?,?,?,?)",
            (new_id, camera_id, camera_name, now_str, photo_url)
        )
        print(f"👤 New subject #{new_id} '{name}' (best_sim={best_sim:.2f})")
        return new_id, True, False

# ─── Telegram ─────────────────────────────────────────────────────────────────

def send_telegram(chat_id, frame, caption):
    _, buf = cv2.imencode('.jpg', frame)
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": ("snap.jpg", buf.tobytes(), "image/jpeg")}
        )
        data = r.json()
        print(f"✅ Telegram -> {chat_id}")
        if data.get("ok"):
            return data["result"]["message_id"]
    except Exception as e:
        print(f"❌ Telegram error: {e}")
    return None

def resolve_chat_id(username):
    if not username:
        return None
    clean = username.replace("@", "").strip()
    if clean.lstrip("-").isdigit():
        return clean
    try:
        from database import SessionLocal, UserDB
        db = SessionLocal()
        user = db.query(UserDB).filter(UserDB.username == clean).first()
        db.close()
        if user and user.telegram_chat_id:
            return user.telegram_chat_id
    except Exception as e:
        print(f"DB resolve error: {e}")
    r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates")
    data = r.json()
    for update in data.get("result", []):
        chat = update.get("message", {}).get("chat", {})
        if chat.get("username", "").lower() == clean.lower():
            return str(chat["id"])
    return None

# ─── Zone check ───────────────────────────────────────────────────────────────

def in_zone(p, zone, frame_w, frame_h, grid_cols=16, grid_rows=9):
    if not zone or not zone.get("cells"):
        return True
    cx = (p["x"] + p["w"] // 2) / frame_w
    cy = (p["y"] + p["h"] // 2) / frame_h
    col = int(cx * grid_cols)
    row = int(cy * grid_rows)
    return [row, col] in zone["cells"]

# ─── Detection ────────────────────────────────────────────────────────────────

def detect_frame(frame, detect_classes, conf=0.5):
    m = get_model()
    results = m(frame, verbose=False)[0]
    detections = []
    for box in results.boxes:
        cls = int(box.cls[0])
        confidence = float(box.conf[0])
        cls_name = CLASS_NAMES.get(cls)
        if cls_name and cls_name in detect_classes and confidence >= conf:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append({"class": cls_name, "conf": confidence, "x": x1, "y": y1, "w": x2-x1, "h": y2-y1})
    return detections

def get_stream_size(url):
    try:
        import subprocess, re
        result = subprocess.run([
            "C:/Program Files/Agent/dlls/x64/ffmpeg.exe",
            "-rtsp_transport", "tcp", "-i", url
        ], capture_output=True, text=True, timeout=10)
        match = re.search(r"(\d{3,4})x(\d{3,4})", result.stderr)
        if match:
            return int(match.group(1)), int(match.group(2))
    except:
        pass
    return 1280, 960

# ─── Camera Worker ────────────────────────────────────────────────────────────

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
        self.last_frame = None
        self.error = None
        self.connected = False
        self.detection_buffer = []  # buffer of (frame, detections) for best frame selection
        self.BUFFER_SIZE = 5        # collect 5 frames before picking best

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(f"🎥 Started: {self.camera['name']}")

    def stop(self):
        self.running = False

    def _loop(self):
        import subprocess

        url = self.camera["rtsp_url"]
        w, h = get_stream_size(url)
        print(f"📐 Stream size: {w}x{h}")
        frame_size = w * h * 3

        def open_ffmpeg(url):
            return subprocess.Popen([
                "C:/Program Files/Agent/dlls/x64/ffmpeg.exe", "-hide_banner", "-loglevel", "error",
                "-rtsp_transport", "tcp",
                "-i", url,
                "-vf", "fps=2",
                "-vcodec", "rawvideo",
                "-pix_fmt", "bgr24",
                "-f", "rawvideo", "-"
            ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)

        proc = open_ffmpeg(url)

        while self.running:
            raw = proc.stdout.read(frame_size)
            if len(raw) < frame_size:
                print(f"🔄 Reconnecting: {self.camera['name']}")
                proc.kill()
                time.sleep(5)
                w, h = get_stream_size(url)
                frame_size = w * h * 3
                self.connected = False
                self.error = "Connection failed"
                proc = open_ffmpeg(url)
                continue

            frame = np.frombuffer(raw, np.uint8).reshape((h, w, 3))
            self.last_frame = frame
            self.connected = True
            self.error = None

            fh, fw = frame.shape[:2]
            detections = detect_frame(frame, self.camera.get("detect_classes", ["person"]))
            in_zone_det = [d for d in detections if in_zone(d, self.camera.get("zone"), fw, fh)]
            now = time.time()

            if in_zone_det and not self.present:
                self.present = True
                self.alert_count = 0
                self.detection_buffer = []

            # Collect frames into buffer to find best shot
            if in_zone_det and self.present:
                self.detection_buffer.append((frame.copy(), in_zone_det))
                if len(self.detection_buffer) > self.BUFFER_SIZE:
                    self.detection_buffer.pop(0)

            if in_zone_det and self.present:
                if now - self.last_alert > self.COOLDOWN and self.alert_count < self.MAX_ALERTS:
                    self.last_alert = now
                    self.alert_count += 1
                    # Pick best frame: largest total bbox area = object closest/most visible
                    best_frame = frame
                    best_dets = in_zone_det
                    if self.detection_buffer:
                        best_score = 0
                        for buf_frame, buf_dets in self.detection_buffer:
                            score = sum(d["w"] * d["h"] for d in buf_dets)
                            if score > best_score:
                                best_score = score
                                best_frame = buf_frame
                                best_dets = buf_dets
                        self.detection_buffer = []
                    in_zone_det = best_dets
                    frame = best_frame
                    cls_names = list(set(d["class"] for d in in_zone_det))
                    caption = f"🚨 {self.camera['name']}: {', '.join(cls_names)} detected"
                    print(f"🔴 {caption}")

                    try:
                        from database import SessionLocal, EventDB
                        from datetime import datetime
                        from photo_service import upload_frame, upload_subject_crop, upload_subject_crop
                        import sqlite3

                        photo_url = upload_frame(frame, self.camera["name"])
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # ── Subject recognition (Premium only) ──────────────
                        _uid = self.camera.get("user_id")
                        _conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
                        _urow = _conn.execute(
                            "SELECT plan FROM users WHERE id=?", (_uid,)
                        ).fetchone()
                        _plan = _urow[0] if _urow else "free"

                        if _plan == "premium" and _uid:
                            for _det in in_zone_det:
                                # Crop with 30% padding
                                _px = int(_det["w"] * 0.3)
                                _py = int(_det["h"] * 0.3)
                                x1 = max(0, _det["x"] - _px)
                                y1 = max(0, _det["y"] - _py)
                                x2 = min(frame.shape[1], _det["x"] + _det["w"] + _px)
                                y2 = min(frame.shape[0], _det["y"] + _det["h"] + _py)
                                _crop = frame[y1:y2, x1:x2]
                                if _crop.size == 0:
                                    continue
                                _crop_url = upload_subject_crop(_crop, f"subject_{self.camera['name']}")
                                subj_id, is_new, is_recurring = find_or_create_subject(
                                    _conn,
                                    _uid,
                                    self.camera["id"],
                                    self.camera["name"],
                                    _det["class"],
                                    _crop,
                                    _crop_url,
                                    now_str
                                )
                                # If recurring and has a name → send named alert
                                if is_recurring:
                                    _name_row = _conn.execute(
                                        "SELECT name, seen_count FROM subjects WHERE id=?", (subj_id,)
                                    ).fetchone()
                                    if _name_row:
                                        _name, _count = _name_row
                                        if _name and not _name.startswith("Unknown"):
                                            caption = f"👤 {_name} detected at {self.camera['name']} (seen {_count}×)"
                                        else:
                                            caption = f"🔄 {self.camera['name']}: recurring {_det['class']} detected (seen {_count}×)"

                            _conn.commit()
                        _conn.close()

                        # ── Telegram / SMS alerts ────────────────────────────
                        tg_chat_id = None
                        tg_msg_id = None
                        _sq_conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
                        _user = _sq_conn.execute(
                            "SELECT telegram_chat_id, phone FROM users WHERE id=?", (_uid,)
                        ).fetchone()
                        _sq_conn.close()

                        _tg_target = self.camera.get("notify_telegram") or (_user[0] if _user else None)
                        _phone_target = self.camera.get("notify_sms") or (_user[1] if _user else None)

                        if _tg_target:
                            chat_id = resolve_chat_id(_tg_target)
                            if chat_id:
                                tg_chat_id = chat_id
                                tg_msg_id = send_telegram(chat_id, frame, caption)

                        # ── Save event ───────────────────────────────────────
                        db = SessionLocal()
                        event = EventDB(
                            camera_id=self.camera["id"],
                            camera_name=self.camera["name"],
                            detected=", ".join(set(d["class"] for d in in_zone_det)),
                            confidence=f"{max(d['conf'] for d in in_zone_det):.2f}",
                            timestamp=now_str,
                            photo_url=photo_url,
                            telegram_chat_id=tg_chat_id,
                            telegram_message_id=tg_msg_id
                        )
                        db.add(event)
                        db.commit()
                        db.close()

                        # ── SMS ──────────────────────────────────────────────
                        if _phone_target:
                            try:
                                from sms_service import send_sms
                                msg = caption
                                if photo_url:
                                    msg += f" Photo: {photo_url}"
                                send_sms(_phone_target, msg)
                            except Exception as e:
                                print(f"❌ SMS error: {e}")

                        # ── Email ────────────────────────────────────────────
                        if self.camera.get("notify_email"):
                            try:
                                from email_service import send_alert_email
                                send_alert_email(
                                    self.camera["notify_email"],
                                    self.camera["name"],
                                    ", ".join(set(d["class"] for d in in_zone_det)),
                                    f"{max(d['conf'] for d in in_zone_det):.2f}"
                                )
                            except Exception as e:
                                print(f"❌ Email error: {e}")

                    except Exception as e:
                        import traceback
                        print(f"❌ Event save error: {e}")
                        traceback.print_exc()

            elif not in_zone_det and self.present:
                if now - self.last_seen > self.EXIT_DELAY:
                    self.present = False
                    self.alert_count = 0
                    print(f"✅ Clear: {self.camera['name']}")

            if in_zone_det:
                self.last_seen = now

        proc.kill()

# ─── Worker management ────────────────────────────────────────────────────────

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
    return {
        cam_id: {
            "name": w.camera["name"],
            "present": w.present,
            "running": w.running,
            "connected": w.connected,
            "error": w.error
        }
        for cam_id, w in workers.items()
    }

# Run schema migration on import
ensure_db_schema()
