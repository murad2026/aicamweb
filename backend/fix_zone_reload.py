content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
old = '''            # Detect in thread pool to avoid blocking event loop
            print(f'🔍 Running detection on frame', flush=True)
            import asyncio
            from engine import detect_frame, in_zone
            loop = asyncio.get_event_loop()
            fh, fw = frame.shape[:2]
            detections = await loop.run_in_executor(None, detect_frame, frame, camera_dict.get("detect_classes", ["person"]))
            in_zone_det = [d for d in detections if in_zone(d, camera_dict.get("zone"), fw, fh)]
            print(f'🔍 Detections: {len(detections)}, in_zone: {len(in_zone_det)}, zone set: {bool(camera_dict.get("zone"))}', flush=True)'''

new = '''            # Reload camera config from DB to get latest zone
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

content = content.replace(old, new)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
