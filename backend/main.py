from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from database import get_db, CameraDB, Base, engine
from auth import hash_password, verify_password, create_token, get_current_user

app = FastAPI(title="AI Any Camera")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Zone(BaseModel):
    cells: List[List[int]]

class CameraCreate(BaseModel):
    name: str
    rtsp_url: str
    brand: str
    zone: Optional[Zone] = None
    detect_classes: List[str] = ["person"]
    name: Optional[str] = None
    notify_telegram: Optional[str] = None
    notify_email: Optional[str] = None

@app.get("/api/health")
def root():
    return {"app": "AI Any Camera", "status": "running"}

class AutoAddRequest(BaseModel):
    ip: str
    username: str
    password: str
    detect_classes: List[str] = ["person"]
    name: Optional[str] = None

@app.post("/cameras/auto-add")
def auto_add_camera(req: AutoAddRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    plan = getattr(current_user, "plan", "free") or "free"
    cam_count = db.query(CameraDB).filter(CameraDB.user_id == current_user.id).count()
    if plan == "free" and cam_count >= 1:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Free plan allows 1 camera only")
    if plan == "pro" and cam_count >= 5:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Pro plan allows 5 cameras only")
    from scanner import test_rtsp
    result = test_rtsp(req.ip, req.username, req.password, "auto")
    if not result.get("success"):
        axis_url = f"rtsp://{req.username}:{req.password}@{req.ip}/axis-media/media.amp?videocodec=h264"
        import cv2
        try:
            cap = cv2.VideoCapture(axis_url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            ret, _ = cap.read()
            cap.release()
            if ret:
                result = {"success": True, "rtsp_url": axis_url, "brand": "axis"}
        except:
            pass
    if not result.get("success"):
        raise HTTPException(status_code=400, detail="Cannot connect to camera. Check IP, username and password.")
    existing = db.query(CameraDB).filter(CameraDB.rtsp_url == result["rtsp_url"], CameraDB.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Camera already added.")
    name = req.name or f"Camera {req.ip}"
    db_cam = CameraDB(
        user_id=current_user.id,
        name=name,
        rtsp_url=result["rtsp_url"],
        brand=result["brand"],
        detect_classes=req.detect_classes,
    )
    db.add(db_cam)
    db.commit()
    db.refresh(db_cam)
    from engine import start_camera
    start_camera({"id": db_cam.id, "name": db_cam.name, "rtsp_url": db_cam.rtsp_url,
                  "detect_classes": db_cam.detect_classes, "zone": db_cam.zone,
                  "notify_telegram": db_cam.notify_telegram, "notify_sms": db_cam.notify_sms,
                  "notify_email": db_cam.notify_email, "push_token": None, "user_id": db_cam.user_id})
    return {"success": True, "camera": {"id": db_cam.id, "name": db_cam.name, "brand": result["brand"], "rtsp_url": result["rtsp_url"]}}

@app.post("/cameras")
def add_camera(camera: CameraCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(CameraDB).filter(CameraDB.rtsp_url == camera.rtsp_url, CameraDB.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Camera already exists: {existing.name}")
    plan = getattr(current_user, "plan", "free") or "free"
    cam_count = db.query(CameraDB).filter(CameraDB.user_id == current_user.id).count()
    if plan == "free" and cam_count >= 1:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Free plan allows 1 camera only")
    if plan == "pro" and cam_count >= 5:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Pro plan allows 5 cameras only")
    if plan == "free" and camera.zone:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Zone detection requires Pro plan")
    db_cam = CameraDB(
        user_id=current_user.id,
        name=camera.name,
        rtsp_url=camera.rtsp_url,
        brand=camera.brand,
        zone=camera.zone.dict() if camera.zone else None,
        detect_classes=camera.detect_classes,
        notify_telegram=camera.notify_telegram,
        notify_email=camera.notify_email
    )
    db.add(db_cam)
    db.commit()
    db.refresh(db_cam)
    from engine import start_camera
    start_camera({"id": db_cam.id, "name": db_cam.name, "rtsp_url": db_cam.rtsp_url,
                  "detect_classes": db_cam.detect_classes, "zone": db_cam.zone,
                  "notify_telegram": db_cam.notify_telegram, "notify_sms": db_cam.notify_sms,
                  "notify_email": db_cam.notify_email, "push_token": None, "user_id": db_cam.user_id})
    return db_cam

@app.get("/cameras")
def list_cameras(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cameras = db.query(CameraDB).filter(CameraDB.user_id == current_user.id).all()
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    result = []
    for cam in cameras:
        new_events = conn.execute("SELECT COUNT(*) FROM events WHERE camera_id=? AND viewed=0", (cam.id,)).fetchone()[0]
        total_events = conn.execute("SELECT COUNT(*) FROM events WHERE camera_id=?", (cam.id,)).fetchone()[0]
        cam_dict = {c.name: getattr(cam, c.name) for c in cam.__table__.columns}
        cam_dict["new_events"] = new_events
        cam_dict["total_events"] = total_events
        result.append(cam_dict)
    conn.close()
    return result

@app.get("/cameras/{cam_id}")
def get_camera(cam_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id, CameraDB.user_id == current_user.id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam

@app.delete("/cameras/{cam_id}")
def delete_camera(cam_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id, CameraDB.user_id == current_user.id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    db.delete(cam)
    db.commit()
    return {"deleted": cam_id}

import cv2
import base64


@app.post("/cameras/{cam_id}/snapshot")
async def post_snapshot(cam_id: int, request: Request, db: Session = Depends(get_db)):
    """Receive snapshot from agent tunnel"""
    data = await request.json()
    image_b64 = data.get("image")
    if not image_b64:
        raise HTTPException(status_code=400, detail="No image")
    # Store in memory
    tunnel_snapshots[cam_id] = image_b64
    return {"ok": True}


@app.get("/cameras/{cam_id}/request_snapshot")
async def request_snapshot(cam_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Ask agent to send a snapshot"""
    ws = active_tunnels.get(cam_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Camera agent not connected")
    await ws.send_text(json.dumps({"type": "get_snapshot"}))
    return {"ok": True, "eta_seconds": 3}

@app.get("/cameras/{cam_id}/snapshot")
def get_snapshot(cam_id: int, db: Session = Depends(get_db)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    # Check tunnel snapshot first
    if cam.id in tunnel_snapshots:
        return {"image": f"data:image/jpeg;base64,{tunnel_snapshots[cam.id]}"}
    worker = workers.get(cam.id)
    if worker and worker.last_frame is not None:
        _, buf = cv2.imencode('.jpg', worker.last_frame)
        img_base64 = base64.b64encode(buf.tobytes()).decode()
        return {"image": f"data:image/jpeg;base64,{img_base64}", "width": worker.last_frame.shape[1], "height": worker.last_frame.shape[0]}
    import subprocess, tempfile, os
    ffmpeg_path = "C:/Program Files/Agent/dlls/x64/ffmpeg.exe"
    if not os.path.exists(ffmpeg_path):
        ffmpeg_path = "ffmpeg"
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmpfile = tmp.name
    try:
        result = subprocess.run([
            ffmpeg_path, "-y", "-hide_banner", "-loglevel", "error",
            "-rtsp_transport", "tcp", "-buffer_size", "1024000",
            "-max_delay", "5000000", "-i", cam.rtsp_url,
            "-frames:v", "1", "-update", "1", tmpfile
        ], timeout=15, capture_output=True)
        if not os.path.exists(tmpfile) or os.path.getsize(tmpfile) == 0:
            err = result.stderr.decode() if result.stderr else "no stderr"
            raise HTTPException(status_code=500, detail=f"Cannot connect: {err}")
        with open(tmpfile, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        return {"image": f"data:image/jpeg;base64,{img_base64}", "width": 1920, "height": 1080}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Camera timeout")
    finally:
        if os.path.exists(tmpfile):
            os.unlink(tmpfile)

class ZoneUpdate(BaseModel):
    cells: List[List[int]]

@app.put("/cameras/{cam_id}/zone")
def update_zone(cam_id: int, zone: ZoneUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    plan = getattr(current_user, "plan", "free") or "free"
    if plan == "free":
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Zone detection requires Pro plan")
    cam.zone = zone.dict()
    db.commit()
    return {"ok": True}

TELEGRAM_TOKEN = "8575525286:AAGUkWh-ro35d8Pru6tODRv8sw4Ingv35nM"

@app.get("/telegram/resolve/{username}")
def resolve_telegram(username: str):
    import requests as req
    username = username.replace("@", "")
    r = req.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates")
    data = r.json()
    for update in data.get("result", []):
        chat = update.get("message", {}).get("chat", {})
        if chat.get("username", "").lower() == username.lower():
            return {"chat_id": str(chat["id"]), "name": chat.get("first_name", "")}
    raise HTTPException(status_code=404, detail="User not found. Ask them to send /start to the bot first.")

from engine import start_camera, stop_camera, get_status, workers

@app.on_event("startup")
def startup():
    print("Server started - camera workers disabled (using agent v5)")

@app.post("/cameras/{cam_id}/start")
def start_cam(cam_id: int, db: Session = Depends(get_db)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Not found")
    start_camera({"id": cam.id, "name": cam.name, "rtsp_url": cam.rtsp_url,
                  "detect_classes": cam.detect_classes, "zone": cam.zone,
                  "notify_telegram": cam.notify_telegram, "notify_sms": cam.notify_sms,
                  "notify_email": cam.notify_email, "push_token": None, "user_id": cam.user_id})
    return {"started": cam_id}

@app.post("/cameras/{cam_id}/stop")
def stop_cam(cam_id: int):
    stop_camera(cam_id)
    return {"stopped": cam_id}

@app.get("/status")
def status():
    return get_status()

from database import EventDB

@app.get("/events")
def get_events(db: Session = Depends(get_db)):
    return db.query(EventDB).order_by(EventDB.id.desc()).limit(100).all()

@app.get("/events/{cam_id}")
def get_camera_events(cam_id: int, db: Session = Depends(get_db)):
    return db.query(EventDB).filter(EventDB.camera_id == cam_id).order_by(EventDB.id.desc()).limit(50).all()

@app.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(EventDB).filter(EventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"deleted": event_id}

@app.delete("/events/camera/{cam_id}")
def delete_camera_events(cam_id: int, db: Session = Depends(get_db)):
    db.query(EventDB).filter(EventDB.camera_id == cam_id).delete()
    db.commit()
    return {"deleted": cam_id}

@app.post("/events/{cam_id}/mark-viewed")
def mark_events_viewed(cam_id: int, current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("UPDATE events SET viewed=1 WHERE camera_id=?", (cam_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

from database import UserDB
from pydantic import BaseModel as PydanticBase
import secrets
from email_service import send_verification_email, send_password_reset_email

class RegisterRequest(PydanticBase):
    email: str
    username: str = ''
    password: str

class LoginRequest(PydanticBase):
    email: str
    password: str

@app.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    verify_token = secrets.token_urlsafe(32)
    import re
    base_username = re.sub(r'[^a-z0-9]', '', req.email.split('@')[0].lower()) or 'user'
    username = base_username
    suffix = 1
    while db.query(UserDB).filter(UserDB.username == username).first():
        username = f"{base_username}{suffix}"
        suffix += 1
    user = UserDB(email=req.email, username=username, hashed_password=hash_password(req.password), verify_token=verify_token, is_verified=0)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        if "username" in str(e):
            raise HTTPException(status_code=400, detail="Username already taken")
        if "email" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=400, detail="Registration failed")
    send_verification_email(user.email, user.username, verify_token)
    return {"message": "Check your email to verify your account"}

@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(user.id)})
    return {"token": token, "user": {"id": user.id, "email": user.email, "username": user.username}}

@app.get("/auth/me")
def me(current_user: UserDB = Depends(get_current_user)):
    plan = getattr(current_user, "plan", "free") or "free"
    cam_count = 0
    try:
        from database import SessionLocal
        db = SessionLocal()
        cam_count = db.query(CameraDB).filter(CameraDB.user_id == current_user.id).count()
        db.close()
    except: pass
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "is_verified": current_user.is_verified,
        "telegram_chat_id": current_user.telegram_chat_id,
        "phone": current_user.phone,
        "phone_verified": getattr(current_user, "phone_verified", 0),
        "plan": plan,
        "cam_count": cam_count,
        "new_subjects": __import__("sqlite3").connect("C:/aianycam/backend/ai-any-camera.db").execute("SELECT COUNT(*) FROM subjects WHERE user_id=? AND viewed=0", (current_user.id,)).fetchone()[0] if plan == "premium" else 0
    }

@app.post("/auth/upgrade")
def upgrade_plan(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    plan = data.get("plan")
    if plan not in ["pro", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid plan")
    current_user.plan = plan
    db.commit()
    return {"ok": True, "plan": plan}

@app.get("/auth/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.verify_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.is_verified = 1
    user.verify_token = None
    db.commit()
    return {"message": "Email verified successfully"}

@app.post("/auth/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        db.commit()
        send_password_reset_email(user.email, token)
    return {"message": "If email exists, reset link sent"}

class ResetPasswordRequest(PydanticBase):
    token: str
    password: str

@app.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.reset_token == req.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.hashed_password = hash_password(req.password)
    user.reset_token = None
    db.commit()
    return {"message": "Password reset successfully"}

class ChangePasswordRequest(PydanticBase):
    current_password: str
    new_password: str

@app.post("/auth/change-password")
def change_password(req: ChangePasswordRequest, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    if not verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(req.new_password)
    db.commit()
    return {"message": "Password changed"}

@app.post("/auth/update-profile")
def update_profile(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if "email" in data and data["email"]:
        existing = db.query(UserDB).filter(UserDB.email == data["email"]).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = data["email"]
    if "phone" in data:
        current_user.phone = data["phone"] or None
    if "telegram_username" in data:
        current_user.notify_telegram = data["telegram_username"] or None
    db.commit()
    return {"ok": True}

import random

@app.post("/auth/send-phone-verify")
def send_phone_verify(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    phone = data.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="Phone required")
    code = str(random.randint(100000, 999999))
    from datetime import datetime
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("DELETE FROM phone_verify_codes WHERE user_id=?", (current_user.id,))
    conn.execute("INSERT INTO phone_verify_codes (user_id, phone, code, created_at) VALUES (?,?,?,?)",
                 (current_user.id, phone, code, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    from sms_service import send_sms
    send_sms(phone, f"Your AI Any Camera verification code: {code}")
    return {"ok": True}

@app.post("/auth/verify-phone")
def verify_phone(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    code = data.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code required")
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    row = conn.execute("SELECT phone, code, created_at FROM phone_verify_codes WHERE user_id=? ORDER BY id DESC LIMIT 1",
                       (current_user.id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=400, detail="No verification code found")
    from datetime import datetime
    created = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - created).seconds > 600:
        raise HTTPException(status_code=400, detail="Code expired")
    if row[1] != code:
        raise HTTPException(status_code=400, detail="Invalid code")
    current_user.phone = row[0]
    current_user.phone_verified = 1
    db.commit()
    return {"ok": True, "phone": row[0]}

@app.delete("/auth/delete-account")
def delete_account(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db.query(CameraDB).filter(CameraDB.user_id == current_user.id).delete()
    db.delete(current_user)
    db.commit()
    return {"ok": True}

@app.post('/push-token')
def save_push_token(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    current_user.push_token = data.get('token')
    db.commit()
    return {'ok': True}

@app.get("/subjects")
def get_subjects(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    rows = conn.execute("SELECT id, name, class, photo_url, first_seen, last_seen, seen_count, camera_id FROM subjects WHERE user_id=? ORDER BY last_seen DESC", (current_user.id,)).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "class": r[2], "photo_url": r[3], "first_seen": r[4], "last_seen": r[5], "seen_count": r[6], "camera_id": r[7]} for r in rows]

@app.put("/subjects/{subject_id}")
def update_subject(subject_id: int, data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("UPDATE subjects SET name=? WHERE id=? AND user_id=?", (data.get("name"), subject_id, current_user.id))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/subjects/mark-viewed")
def mark_subjects_viewed(current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("UPDATE subjects SET viewed=1 WHERE user_id=?", (current_user.id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("DELETE FROM subjects WHERE id=? AND user_id=?", (subject_id, current_user.id))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/recognized")
def get_recognized(current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    rows = conn.execute(
        "SELECT id, name, class, photo_url, first_seen, last_seen, seen_count, camera_id FROM subjects WHERE user_id=? AND seen_count > 1 ORDER BY last_seen DESC",
        (current_user.id,)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "class": r[2], "photo_url": r[3], "first_seen": r[4], "last_seen": r[5], "seen_count": r[6], "camera_id": r[7]} for r in rows]

@app.get("/subjects/{subject_id}/sightings")
def get_subject_sightings(subject_id: int, current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    owner = conn.execute("SELECT user_id FROM subjects WHERE id=?", (subject_id,)).fetchone()
    if not owner or owner[0] != current_user.id:
        conn.close()
        raise HTTPException(status_code=404, detail="Not found")
    rows = conn.execute(
        "SELECT id, camera_id, camera_name, timestamp, photo_url FROM subject_sightings WHERE subject_id=? ORDER BY timestamp DESC LIMIT 50",
        (subject_id,)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "camera_id": r[1], "camera_name": r[2], "timestamp": r[3], "photo_url": r[4]} for r in rows]

@app.post("/chat/escalate")
async def escalate_to_human(data: dict, current_user = Depends(get_current_user)):
    from sms_service import send_sms
    username = getattr(current_user, "username", "Unknown")
    email = getattr(current_user, "email", "Unknown")
    plan = getattr(current_user, "plan", "free") or "free"
    last_message = data.get("last_message", "")
    msg = f"AI Any Camera LEAD: {username} ({email}, {plan} plan) wants to talk. Last message: {last_message}"
    try:
        send_sms("+16173724119", msg)
        return {"ok": True}
    except Exception as e:
        print(f"Escalation SMS error: {e}")
        return {"ok": False}

ANTHROPIC_KEY = "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"
AI_SYSTEM = """You are an AI assistant for AI Any Camera - a smart security camera monitoring service. Help users with: finding camera IP (check router at 192.168.1.1), default credentials (Hikvision: admin/12345, Dahua: admin/admin, Axis: root/pass), troubleshooting offline cameras, setting up alerts. Plans: Free 1 camera, Pro $19/mo 5 cameras, Premium $49/mo unlimited+subjects. Enterprise: 40+ cameras, custom pricing, contact sales. Be helpful and concise."""

@app.post("/chat")
async def chat_endpoint(data: dict):
    import httpx
    messages = data.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="No messages")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 500, "system": AI_SYSTEM, "messages": messages}
        )
        result = r.json()
        text = result.get("content", [{}])[0].get("text", "Sorry, try again.")
        return {"reply": text}

CRISP_WEBSITE_ID = "4d8501f9-ee54-4f41-8f91-e69937105b82"
CRISP_API_ID = "0a06d6f8-2cfa-4148-8f53-949f2f31dded"
CRISP_API_KEY = "071b4d0b9b43bb34fb03e0055955375f41c90276920028eeb5feeb792f3ced77"

CRISP_SYSTEM = """You are an AI assistant for AI Any Camera — a smart security camera monitoring platform.
You help users with connecting cameras, setting up alerts, and understanding plans.
Plans: Free (1 camera), Pro $19/mo (5 cameras), Premium $49/mo (unlimited + AI subject recognition), Enterprise (40+ cameras, custom pricing).
When users want Enterprise or want to talk to a human, tell them you're connecting them with the team now."""

HUMAN_KEYWORDS = ["talk to human", "real person", "live agent", "human agent", "speak with someone", "talk to agent", "enterprise", "custom quote", "contact sales"]

@app.post("/crisp/webhook")
async def crisp_webhook(request: Request):
    import httpx
    try:
        data = await request.json()
    except:
        return {"ok": True}
    event = data.get("event", "")
    if event != "message:send":
        return {"ok": True}
    msg_data = data.get("data", {})
    content = msg_data.get("content", "")
    session_id = msg_data.get("session_id", "")
    origin = msg_data.get("origin", "")
    if origin in ("operator", "bot"):
        return {"ok": True}
    if not content or not session_id:
        return {"ok": True}
    content_lower = content.lower()
    wants_human = any(kw in content_lower for kw in HUMAN_KEYWORDS)
    if wants_human:
        reply = "I'm connecting you with our team right now! 🙋 You'll hear from us shortly."
        try:
            from sms_service import send_sms
            send_sms("+16173724119", f"AI Any Camera LEAD via Crisp: {content[:100]}")
        except Exception as e:
            print(f"SMS error: {e}")
    else:
        messages_for_ai = [{"role": "user", "content": content}]
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                    json={"model": "claude-haiku-4-5-20251001", "max_tokens": 300, "system": CRISP_SYSTEM, "messages": messages_for_ai}
                )
                result = r.json()
                reply = result.get("content", [{}])[0].get("text", "Sorry, try again.")
        except Exception as e:
            print(f"AI error: {e}")
            reply = "Sorry, I'm having trouble right now. Please try again."
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/message",
                auth=(CRISP_API_ID, CRISP_API_KEY),
                headers={"X-Crisp-Tier": "plugin", "Content-Type": "application/json"},
                json={"type": "text", "content": reply, "from": "operator", "origin": "chat"}
            )
    except Exception as e:
        print(f"Crisp reply error: {e}")
    return {"ok": True}

from scanner import scan_network, test_rtsp

@app.get("/scan")
def scan():
    cameras = scan_network()
    return {"cameras": cameras}

ADMIN_PASSWORD = "AiAnyCam2026!"

@app.get("/admin/stats")
def admin_stats(password: str, db: Session = Depends(get_db)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Forbidden")
    import sqlite3, psutil, os
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    
    users = conn.execute("SELECT id, email, username, plan, created_at FROM users ORDER BY id DESC").fetchall()
    users_data = []
    for u in users:
        cam_count = conn.execute("SELECT COUNT(*) FROM cameras WHERE user_id=?", (u[0],)).fetchone()[0]
        event_count = conn.execute("SELECT COUNT(*) FROM events WHERE camera_id IN (SELECT id FROM cameras WHERE user_id=?)", (u[0],)).fetchone()[0]
        users_data.append({
            "id": u[0], "email": u[1], "username": u[2],
            "plan": u[3] or "free", "created_at": u[4],
            "cam_count": cam_count, "event_count": event_count
        })
    
    total_cameras = conn.execute("SELECT COUNT(*) FROM cameras").fetchone()[0]
    total_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    total_subjects = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    conn.close()
    
    # System stats
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("C:/")
    
    # Camera workers status
    camera_status = get_status()
    
    # SMS gateway check
    sms_ok = False
    try:
        import requests as req
        r = req.get("http://192.168.2.6:8080", timeout=3)
        sms_ok = r.status_code < 500
    except:
        pass
    
    return {
        "users": users_data,
        "totals": {
            "users": len(users_data),
            "cameras": total_cameras,
            "events": total_events,
            "subjects": total_subjects
        },
        "system": {
            "cpu_percent": cpu,
            "ram_used_gb": round(ram.used / 1024**3, 1),
            "ram_total_gb": round(ram.total / 1024**3, 1),
            "ram_percent": ram.percent,
            "disk_used_gb": round(disk.used / 1024**3, 1),
            "disk_total_gb": round(disk.total / 1024**3, 1),
            "disk_percent": round(disk.used / disk.total * 100, 1)
        },
        "services": {
            "backend": True,
            "sms_gateway": sms_ok,
            "cameras_active": len([c for c in camera_status.get("cameras", []) if c.get("status") == "running"]),
            "cameras_total": total_cameras
        }
    }

@app.post("/admin/set-plan")
def admin_set_plan(data: dict, db: Session = Depends(get_db)):
    if data.get("password") != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(UserDB).filter(UserDB.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.plan = data.get("plan")
    db.commit()
    return {"ok": True}




@app.get("/admin")
def admin_page():
    from fastapi.responses import FileResponse
    import os
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build', 'index.html'))


class AlertsUpdate(BaseModel):
    notify_telegram: Optional[str] = None
    notify_sms: Optional[str] = None
    notify_email: Optional[str] = None

@app.put("/cameras/{cam_id}/alerts")
def update_alerts(cam_id: int, data: AlertsUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id, CameraDB.user_id == current_user.id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    cam.notify_telegram = data.notify_telegram
    cam.notify_sms = data.notify_sms
    cam.notify_email = data.notify_email
    db.commit()
    # Restart camera worker with new settings
    from engine import start_camera
    start_camera({"id": cam.id, "name": cam.name, "rtsp_url": cam.rtsp_url,
                  "detect_classes": cam.detect_classes or ["person"],
                  "zone": cam.zone, "notify_telegram": cam.notify_telegram,
                  "notify_sms": cam.notify_sms, "notify_email": cam.notify_email,
                  "push_token": None, "user_id": cam.user_id})
    return {"ok": True}


@app.post("/api/agent/event")
async def agent_event(request: Request, db: Session = Depends(get_db)):
    """Receive detection event from local agent (Raspberry Pi)"""
    data = await request.json()
    
    # Verify token
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    from auth import get_current_user_by_token
    user = get_current_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    camera_id = data.get("camera_id")
    cam = db.query(CameraDB).filter(CameraDB.id == camera_id, CameraDB.user_id == user.id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    detected = data.get("detected", "person")
    confidence = data.get("confidence", "0.90")
    photo_b64 = data.get("photo")
    
    # Upload photo
    photo_url = None
    print(f"photo_b64 received: {bool(photo_b64)}", flush=True)
    if photo_b64:
        try:
            import base64, cv2, numpy as np, tempfile, os
            img_bytes = base64.b64decode(photo_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                from photo_service import upload_frame
                photo_url = upload_frame(frame, cam.name)
                print(f"Photo URL: {photo_url}", flush=True)
        except Exception as e:
            print(f"Photo upload error: {e}")
    
    # Save event
    from datetime import datetime
    from database import EventDB
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_time = datetime.now().strftime("%H:%M:%S")
    
    event = EventDB(
        camera_id=cam.id, camera_name=cam.name,
        detected=detected, confidence=confidence,
        timestamp=now_str, photo_url=photo_url
    )
    db.add(event); db.commit()
    
    # Send alerts
    caption = f"🚨 {cam.name}: {detected} detected at {now_time}"
    
    if cam.notify_telegram:
        try:
            from engine import send_telegram, resolve_chat_id
            chat_id = resolve_chat_id(cam.notify_telegram)
            if chat_id and frame is not None:
                send_telegram(chat_id, frame, caption)
        except Exception as e:
            print(f"Telegram error: {e}")
    
    if cam.notify_sms:
        try:
            from sms_service import send_sms
            msg = caption
            if photo_url:
                import re, time as _t
                match = re.search(r'/v(\d+)/', photo_url)
                if match:
                    photo_ts = int(match.group(1))
                    age = int(_t.time()) - photo_ts
                    if age > 300:
                        print(f"Photo too old ({age}s), skipping URL")
                        photo_url = None
                if photo_url:
                    msg += f" {photo_url}" if photo_url else ""

            print(f'SMS MESSAGE: {msg}', flush=True)
            send_sms(cam.notify_sms, msg)
        except Exception as e:
            print(f"SMS error: {e}")
    
    print(f"✅ Agent event: {caption}", flush=True)
    return {"ok": True, "event_id": event.id}

@app.post("/api/agent/snapshot")
async def agent_snapshot(request: Request, db: Session = Depends(get_db)):
    """Receive snapshot from agent for zone editor / live view"""
    data = await request.json()
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    from auth import get_current_user_by_token
    user = get_current_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    camera_id = data.get("camera_id")
    image_b64 = data.get("image")
    if image_b64:
        tunnel_snapshots[camera_id] = image_b64
    return {"ok": True}

@app.get("/agent/cameras")
def agent_cameras(db: Session = Depends(get_db)):
    """Get cameras list for agent - authenticated by token in header"""
    from fastapi import Header
    token = None
    return {"error": "use /cameras endpoint with Bearer token"}


import threading as _threading
import time as _time

def _cloudinary_cleanup():
    """Delete old photos from Cloudinary based on user plan"""
    while True:
        try:
            _time.sleep(3600)  # Run every hour
            import cloudinary.api
            from database import SessionLocal, EventDB
            from sqlalchemy import func
            
            db = SessionLocal()
            now = _time.time()
            
            # Get all events with photo_url
            events = db.query(EventDB).filter(EventDB.photo_url != None).all()
            
            for event in events:
                if not event.photo_url:
                    continue
                import re
                match = re.search(r'/v(\d+)/', event.photo_url)
                if not match:
                    continue
                photo_ts = int(match.group(1))
                age_days = (now - photo_ts) / 86400
                
                # Get user plan
                from database import CameraDB, UserDB
                cam = db.query(CameraDB).filter(CameraDB.id == event.camera_id).first()
                if not cam:
                    continue
                user = db.query(UserDB).filter(UserDB.id == cam.user_id).first()
                plan = user.plan if user else "free"
                
                # Delete based on plan
                max_days = 1 if plan == "free" else 7 if plan == "pro" else 14
                
                if age_days > max_days:
                    try:
                        public_id = re.search(r'/aianycamera/(.+)\.jpg', event.photo_url)
                        if public_id:
                            cloudinary.api.delete_resources([f"aianycamera/{public_id.group(1)}"])
                            print(f"Deleted old photo: {public_id.group(1)}")
                    except Exception as e:
                        pass
            
            db.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

_cleanup_thread = _threading.Thread(target=_cloudinary_cleanup, daemon=True)
_cleanup_thread.start()
print("✅ Cloudinary cleanup started", flush=True)
# Serve frontend
from fastapi.staticfiles import StaticFiles
import os
frontend_build = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
if os.path.exists(frontend_build):
    app.mount('/', StaticFiles(directory=frontend_build, html=True), name='static')

