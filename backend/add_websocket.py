content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

ws_code = '''
# ─── WebSocket Tunnel for Remote Cameras ─────────────────────────────────────

from fastapi import WebSocket, WebSocketDisconnect
import base64, json, numpy as np, cv2, time

active_tunnels = {}  # camera_id -> websocket

@app.websocket("/ws/tunnel/{camera_id}")
async def camera_tunnel(websocket: WebSocket, camera_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    
    # Verify token
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001)
            return
        from auth import get_current_user_by_token
        user = get_current_user_by_token(token, db)
        if not user:
            await websocket.close(code=4001)
            return
        
        cam = db.query(CameraDB).filter(CameraDB.id == camera_id, CameraDB.user_id == user.id).first()
        if not cam:
            await websocket.close(code=4004)
            return
    except Exception as e:
        print(f"WS auth error: {e}")
        await websocket.close(code=4001)
        return

    print(f"🔌 Tunnel connected: camera {camera_id} ({cam.name})")
    active_tunnels[camera_id] = websocket
    
    camera_dict = {
        "id": cam.id, "name": cam.name, "rtsp_url": cam.rtsp_url,
        "user_id": cam.user_id,
        "detect_classes": cam.detect_classes or ["person"],
        "zone": cam.zone,
        "notify_telegram": cam.notify_telegram,
        "notify_sms": cam.notify_sms,
        "notify_email": cam.notify_email,
        "push_token": None,
    }

    last_alert = 0
    COOLDOWN = 60

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") != "frame":
                continue

            # Decode frame
            frame_bytes = base64.b64decode(msg["frame"])
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                continue

            # Detect
            from engine import detect_frame, in_zone
            fh, fw = frame.shape[:2]
            detections = detect_frame(frame, camera_dict.get("detect_classes", ["person"]))
            in_zone_det = [d for d in detections if in_zone(d, camera_dict.get("zone"), fw, fh)]

            now = time.time()
            if in_zone_det and now - last_alert > COOLDOWN:
                last_alert = now
                # Send alert
                await websocket.send_text(json.dumps({"type": "alert", "detections": [{"class": d["class"]} for d in in_zone_det]}))
                
                # Process alert (photo, SMS, Telegram)
                try:
                    from photo_service import upload_frame
                    from datetime import datetime
                    import sqlite3
                    
                    cls_names = list(set(d["class"] for d in in_zone_det))
                    caption = f"🚨 {cam.name}: {', '.join(cls_names)} detected"
                    photo_url = upload_frame(frame, cam.name)
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    from database import SessionLocal, EventDB
                    _db = SessionLocal()
                    event = EventDB(
                        camera_id=cam.id, camera_name=cam.name,
                        detected=", ".join(cls_names),
                        confidence=f"{max(d['conf'] for d in in_zone_det):.2f}",
                        timestamp=now_str, photo_url=photo_url,
                    )
                    _db.add(event); _db.commit(); _db.close()

                    if cam.notify_telegram:
                        from engine import send_telegram, resolve_chat_id
                        chat_id = resolve_chat_id(cam.notify_telegram)
                        if chat_id:
                            send_telegram(chat_id, frame, caption)

                    if cam.notify_sms:
                        from sms_service import send_sms
                        send_sms(cam.notify_sms, caption + (f" Photo: {photo_url}" if photo_url else ""))

                except Exception as e:
                    print(f"Alert error: {e}")
            else:
                await websocket.send_text(json.dumps({"type": "clear"}))

    except WebSocketDisconnect:
        print(f"🔌 Tunnel disconnected: camera {camera_id}")
        active_tunnels.pop(camera_id, None)
    except Exception as e:
        print(f"❌ Tunnel error: {e}")
        active_tunnels.pop(camera_id, None)

'''

# Insert before static files mount
insert_before = "# Serve frontend"
content = content.replace(insert_before, ws_code + insert_before)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
