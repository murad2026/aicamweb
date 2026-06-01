content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

cleanup_code = '''
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
                match = re.search(r\'/v(\\d+)/\', event.photo_url)
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
                        public_id = re.search(r\'/aianycamera/(.+)\\.jpg\', event.photo_url)
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
'''

content = content.replace(
    "print(\"✅ Detection worker started\", flush=True)",
    "print(\"✅ Detection worker disabled\", flush=True)"
)

# Add before serve frontend
content = content.replace(
    "# Serve frontend",
    cleanup_code + "# Serve frontend"
)

open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
