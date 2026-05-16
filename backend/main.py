from fastapi import FastAPI, Depends, HTTPException
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
    notify_telegram: Optional[str] = None
    notify_email: Optional[str] = None

@app.get("/")
def root():
    return {"app": "AI Any Camera", "status": "running"}

@app.post("/cameras")
def add_camera(camera: CameraCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(CameraDB).filter(CameraDB.rtsp_url == camera.rtsp_url, CameraDB.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Camera already exists: {existing.name}")
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
    return db_cam

@app.get("/cameras")
def list_cameras(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(CameraDB).filter(CameraDB.user_id == current_user.id).all()

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import UploadFile, File
from detector import detect_image_bytes

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()
    detections = detect_image_bytes(contents)
    return {"detections": detections}

import cv2
import base64

@app.get("/cameras/{cam_id}/snapshot")
def get_snapshot(cam_id: int, db: Session = Depends(get_db)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    cap = cv2.VideoCapture(cam.rtsp_url)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise HTTPException(status_code=500, detail="Cannot connect to camera")
    _, buf = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buf.tobytes()).decode()
    return {"image": f"data:image/jpeg;base64,{img_base64}", "width": frame.shape[1], "height": frame.shape[0]}

class ZoneUpdate(BaseModel):
    cells: List[List[int]]

@app.put("/cameras/{cam_id}/zone")
def update_zone(cam_id: int, zone: ZoneUpdate, db: Session = Depends(get_db)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
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

from engine import start_camera, stop_camera, get_status
from contextlib import asynccontextmanager

@app.on_event("startup")
def startup():
    from database import SessionLocal
    db = SessionLocal()
    cameras = db.query(CameraDB).all()
    db.close()
    for cam in cameras:
        start_camera({
            "id": cam.id, "name": cam.name, "rtsp_url": cam.rtsp_url,
            "detect_classes": cam.detect_classes or ["person"],
            "zone": cam.zone, "notify_telegram": cam.notify_telegram
        })
    print(f"🚀 Started {len(cameras)} camera workers")

@app.post("/cameras/{cam_id}/start")
def start_cam(cam_id: int, db: Session = Depends(get_db)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Not found")
    start_camera({"id": cam.id, "name": cam.name, "rtsp_url": cam.rtsp_url,
                  "detect_classes": cam.detect_classes, "zone": cam.zone,
                  "notify_telegram": cam.notify_telegram})
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

from auth import hash_password, verify_password, create_token, get_current_user
from database import UserDB
from pydantic import BaseModel as PydanticBase

class RegisterRequest(PydanticBase):
    email: str
    username: str
    password: str

class LoginRequest(PydanticBase):
    email: str
    password: str

@app.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    verify_token = secrets.token_urlsafe(32)
    user = UserDB(email=req.email, username=req.username, hashed_password=hash_password(req.password), verify_token=verify_token, is_verified=0)
    db.add(user)
    db.commit()
    db.refresh(user)
    send_verification_email(user.email, user.username, verify_token)
    token = create_token({"sub": str(user.id)})
    return {"token": token, "user": {"id": user.id, "email": user.email, "username": user.username, "is_verified": 0}}

@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(user.id)})
    return {"token": token, "user": {"id": user.id, "email": user.email, "username": user.username}}

@app.get("/auth/me")
def me(current_user: UserDB = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "username": current_user.username}

from scanner import scan_network, test_rtsp
from auth import hash_password, verify_password, create_token, get_current_user

@app.get("/scan")
def scan():
    cameras = scan_network()
    return {"cameras": cameras}

class TestRTSPRequest(BaseModel):
    ip: str
    username: str
    password: str
    brand: str = "generic"

@app.post("/test-rtsp")
def test_camera(req: TestRTSPRequest):
    result = test_rtsp(req.ip, req.username, req.password, req.brand)
    return result

import secrets
from email_service import send_verification_email, send_password_reset_email

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
