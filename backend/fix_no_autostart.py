content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    '''@app.on_event("startup")
def startup():
    from database import SessionLocal
    db = SessionLocal()
    cameras = db.query(CameraDB).filter(CameraDB.rtsp_url != None, CameraDB.rtsp_url != "").all()
    db.close()
    started = 0
    for cam in cameras:
        try:
            start_camera({
                "id": cam.id, "name": cam.name, "rtsp_url": cam.rtsp_url,
                "detect_classes": cam.detect_classes or ["person"],
                "zone": cam.zone, "notify_telegram": cam.notify_telegram,
                "notify_sms": cam.notify_sms, "notify_email": cam.notify_email,
                "push_token": None, "user_id": cam.user_id
            })
            started += 1
        except Exception as e:
            print(f"Failed to start camera {cam.name}: {e}")
    print(f"Started {started} camera workers")''',
    '''@app.on_event("startup")
def startup():
    print("Server started - camera workers disabled (using agent v5)")'''
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
