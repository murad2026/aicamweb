with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def add_camera(camera: CameraCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(CameraDB).filter(CameraDB.rtsp_url == camera.rtsp_url, CameraDB.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Camera already exists: {existing.name}")'''

new = '''def add_camera(camera: CameraCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(CameraDB).filter(CameraDB.rtsp_url == camera.rtsp_url, CameraDB.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Camera already exists: {existing.name}")
    # Plan limits
    plan = getattr(current_user, "plan", "free") or "free"
    cam_count = db.query(CameraDB).filter(CameraDB.user_id == current_user.id).count()
    if plan == "free" and cam_count >= 1:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Free plan allows 1 camera only")
    if plan == "pro" and cam_count >= 5:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Pro plan allows 5 cameras only")
    # Free plan cannot save zone
    if plan == "free" and camera.zone:
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Zone detection requires Pro plan")'''

content = content.replace(old, new)
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
