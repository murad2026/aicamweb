with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_route = '''
class AutoAddRequest(BaseModel):
    ip: str
    username: str
    password: str
    detect_classes: List[str] = ["person"]

@app.post("/cameras/auto-add")
def auto_add_camera(req: AutoAddRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Check plan limits
    plan = getattr(current_user, "plan", "free") or "free"
    cam_count = db.query(CameraDB).filter(CameraDB.user_id == current_user.id).count()
    if plan == "free" and cam_count >= 1:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Free plan allows 1 camera only")
    if plan == "pro" and cam_count >= 5:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Pro plan allows 5 cameras only")
    # Try all RTSP formats
    from scanner import test_rtsp
    result = test_rtsp(req.ip, req.username, req.password, "auto")
    if not result.get("success"):
        # Also try Axis
        axis_url = f"rtsp://{req.username}:{req.password}@{req.ip}/axis-media/media.amp?videocodec=h264"
        from scanner import test_rtsp as tr
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
    # Check if already exists
    existing = db.query(CameraDB).filter(CameraDB.rtsp_url == result["rtsp_url"], CameraDB.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Camera already added.")
    name = f"Camera {req.ip}"
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
'''

content = content.replace('@app.post("/cameras")', new_route + '\n@app.post("/cameras")')
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
