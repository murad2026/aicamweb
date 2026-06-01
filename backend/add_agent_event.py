content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

new_endpoint = '''
@app.post("/agent/event")
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
    if photo_b64:
        try:
            import base64, cv2, numpy as np, tempfile, os
            img_bytes = base64.b64decode(photo_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                from photo_service import upload_frame
                photo_url = upload_frame(frame, cam.name)
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
                msg += f" Photo: {photo_url}"
            send_sms(cam.notify_sms, msg)
        except Exception as e:
            print(f"SMS error: {e}")
    
    print(f"✅ Agent event: {caption}", flush=True)
    return {"ok": True, "event_id": event.id}

@app.post("/agent/snapshot")
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

'''

content = content.replace(
    "# Serve frontend",
    new_endpoint + "# Serve frontend"
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
