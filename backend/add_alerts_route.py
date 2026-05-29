with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

alerts_route = '''
class AlertsUpdate(BaseModel):
    notify_telegram: Optional[str] = None
    notify_sms: Optional[str] = None
    notify_email: Optional[str] = None

@app.put("/cameras/{cam_id}/alerts")
def update_alerts(cam_id: int, data: AlertsUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cam = db.query(CameraDB).filter(CameraDB.id == cam_id, CameraDB.user_id == current_user.id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    cam.notify_telegram = data.notify_telegram
    cam.notify_sms = data.notify_sms
    cam.notify_email = data.notify_email
    db.commit()
    # Restart camera worker with new settings
    from engine import start_camera
    start_camera({"id": cam.id, "name": cam.name, "rtsp_url": cam.rtsp_url,
                  "detect_classes": cam.detect_classes or ["person"],
                  "zone": cam.zone, "notify_telegram": cam.notify_telegram,
                  "notify_sms": cam.notify_sms, "notify_email": cam.notify_email,
                  "push_token": None, "user_id": cam.user_id})
    return {"ok": True}

'''

if '/cameras/{cam_id}/alerts' not in content:
    content = content.replace('# Serve frontend', alerts_route + '# Serve frontend')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Already exists')
