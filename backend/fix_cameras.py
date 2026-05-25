with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''@app.get("/cameras")
def list_cameras(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(CameraDB).filter(CameraDB.user_id == current_user.id).all()'''

new = '''@app.get("/cameras")
def list_cameras(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cameras = db.query(CameraDB).filter(CameraDB.user_id == current_user.id).all()
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    result = []
    for cam in cameras:
        new_events = conn.execute("SELECT COUNT(*) FROM events WHERE camera_id=? AND viewed=0", (cam.id,)).fetchone()[0]
        total_events = conn.execute("SELECT COUNT(*) FROM events WHERE camera_id=?", (cam.id,)).fetchone()[0]
        cam_dict = {c.name: getattr(cam, c.name) for c in cam.__table__.columns}
        cam_dict["new_events"] = new_events
        cam_dict["total_events"] = total_events
        result.append(cam_dict)
    conn.close()
    return result'''

content = content.replace(old, new)
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
