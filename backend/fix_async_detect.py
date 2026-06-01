content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
old = '''            # Detect
            print(f'🔍 Running detection on frame', flush=True)
            from engine import detect_frame, in_zone
            fh, fw = frame.shape[:2]
            detections = detect_frame(frame, camera_dict.get("detect_classes", ["person"]))
            in_zone_det = [d for d in detections if in_zone(d, camera_dict.get("zone"), fw, fh)]
            print(f'🔍 Detections: {detections}, in_zone: {in_zone_det}, zone: {camera_dict.get("zone")}', flush=True)'''

new = '''            # Detect in thread pool to avoid blocking event loop
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
