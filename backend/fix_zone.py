with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''@app.put("/cameras/{cam_id}/zone")
def update_zone(cam_id: int, zone: ZoneUpdate, db: Session = Depends(get_db)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    cam.zone = zone.dict()
    db.commit()
    return {"ok": True}'''

new = '''@app.put("/cameras/{cam_id}/zone")
def update_zone(cam_id: int, zone: ZoneUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    plan = getattr(current_user, "plan", "free") or "free"
    if plan == "free":
        raise HTTPException(status_code=403, detail="UPGRADE_REQUIRED: Zone detection requires Pro plan")
    cam.zone = zone.dict()
    db.commit()
    return {"ok": True}'''

content = content.replace(old, new)
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
