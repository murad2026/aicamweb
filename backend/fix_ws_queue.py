content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

# Replace the detection block with just saving frame to queue
old = '''            # Reload camera config from DB to get latest zone
            from database import SessionLocal
            _db = SessionLocal()
            _cam = _db.query(CameraDB).filter(CameraDB.id == camera_id).first()
            if _cam:
                camera_dict["zone"] = _cam.zone
                camera_dict["notify_sms"] = _cam.notify_sms
                camera_dict["notify_telegram"] = _cam.notify_telegram
                camera_dict["notify_email"] = _cam.notify_email
            _db.close()

            # Detect in thread pool to avoid blocking event loop
            print(f'🔍 Running detection on frame', flush=True)
            import asyncio
            from engine import detect_frame, in_zone
            loop = asyncio.get_event_loop()
            fh, fw = frame.shape[:2]
            detections = await loop.run_in_executor(None, detect_frame, frame, camera_dict.get("detect_classes", ["person"]))
            in_zone_det = [d for d in detections if in_zone(d, camera_dict.get("zone"), fw, fh)]
            print(f'🔍 Detections: {len(detections)}, in_zone: {len(in_zone_det)}, zone set: {bool(camera_dict.get("zone"))}', flush=True)'''

new = '''            # Put frame in detection queue (non-blocking)
            detection_queue.put_nowait((camera_id, frame.copy()))
            await websocket.send_text(json.dumps({"type": "ack"}))'''

content = content.replace(old, new)

# Add queue and worker near top
content = content.replace(
    "active_tunnels = {}  # camera_id -> websocket",
    '''active_tunnels = {}  # camera_id -> websocket
import queue as _queue
detection_queue = _queue.Queue(maxsize=10)

def _detection_worker():
    """Background thread for YOLO detection"""
    while True:
        try:
            camera_id, frame = detection_queue.get(timeout=1)
            from database import SessionLocal
            from engine import detect_frame, in_zone
            _db = SessionLocal()
            _cam = _db.query(CameraDB).filter(CameraDB.id == camera_id).first()
            if not _cam:
                _db.close()
                continue
            zone = _cam.zone
            notify_sms = _cam.notify_sms
            notify_telegram = _cam.notify_telegram
            _db.close()

            fh, fw = frame.shape[:2]
            detections = detect_frame(frame, ["person"])
            in_zone_det = [d for d in detections if in_zone(d, zone, fw, fh)]
            print(f"🔍 cam {camera_id}: {len(detections)} detections, {len(in_zone_det)} in zone", flush=True)

            if not in_zone_det:
                continue

            import time
            now = time.time()
            last = _last_alert.get(camera_id, 0)
            if now - last < 60:
                continue
            _last_alert[camera_id] = now

            try:
                from photo_service import upload_frame
                from datetime import datetime
                from database import SessionLocal, EventDB
                cls_names = list(set(d["class"] for d in in_zone_det))
                caption = f"🚨 {_cam.name}: {', '.join(cls_names)} detected"
                photo_url = upload_frame(frame, _cam.name)
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                _db2 = SessionLocal()
                event = EventDB(camera_id=camera_id, camera_name=_cam.name,
                    detected=", ".join(cls_names),
                    confidence=f"{max(d['conf'] for d in in_zone_det):.2f}",
                    timestamp=now_str, photo_url=photo_url)
                _db2.add(event); _db2.commit(); _db2.close()
                if notify_telegram:
                    from engine import send_telegram, resolve_chat_id
                    chat_id = resolve_chat_id(notify_telegram)
                    if chat_id:
                        send_telegram(chat_id, frame, caption)
                if notify_sms:
                    from sms_service import send_sms
                    send_sms(notify_sms, caption + (f" Photo: {photo_url}" if photo_url else ""))
                print(f"🚨 Alert sent: {caption}", flush=True)
            except Exception as e:
                print(f"Alert error: {e}", flush=True)
        except _queue.Empty:
            continue
        except Exception as e:
            print(f"Detection worker error: {e}", flush=True)

_last_alert = {}
import threading as _threading
_det_thread = _threading.Thread(target=_detection_worker, daemon=True)
_det_thread.start()
print("✅ Detection worker started", flush=True)'''
)

# Remove old alert block from websocket
old_alert = '''            now = time.time()
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
                await websocket.send_text(json.dumps({"type": "clear"}))'''

content = content.replace(old_alert, '')

open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
