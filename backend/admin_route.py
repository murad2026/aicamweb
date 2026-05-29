ADMIN_PASSWORD = "AiAnyCam2026!"

@app.get("/admin/stats")
def admin_stats(password: str, db: Session = Depends(get_db)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Forbidden")
    import sqlite3, psutil, os
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    
    users = conn.execute("SELECT id, email, username, plan, created_at FROM users ORDER BY id DESC").fetchall()
    users_data = []
    for u in users:
        cam_count = conn.execute("SELECT COUNT(*) FROM cameras WHERE user_id=?", (u[0],)).fetchone()[0]
        event_count = conn.execute("SELECT COUNT(*) FROM events WHERE camera_id IN (SELECT id FROM cameras WHERE user_id=?)", (u[0],)).fetchone()[0]
        users_data.append({
            "id": u[0], "email": u[1], "username": u[2],
            "plan": u[3] or "free", "created_at": u[4],
            "cam_count": cam_count, "event_count": event_count
        })
    
    total_cameras = conn.execute("SELECT COUNT(*) FROM cameras").fetchone()[0]
    total_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    total_subjects = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    conn.close()
    
    # System stats
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("C:/")
    
    # Camera workers status
    camera_status = get_status()
    
    # SMS gateway check
    sms_ok = False
    try:
        import requests as req
        r = req.get("http://192.168.2.6:8080", timeout=3)
        sms_ok = r.status_code < 500
    except:
        pass
    
    return {
        "users": users_data,
        "totals": {
            "users": len(users_data),
            "cameras": total_cameras,
            "events": total_events,
            "subjects": total_subjects
        },
        "system": {
            "cpu_percent": cpu,
            "ram_used_gb": round(ram.used / 1024**3, 1),
            "ram_total_gb": round(ram.total / 1024**3, 1),
            "ram_percent": ram.percent,
            "disk_used_gb": round(disk.used / 1024**3, 1),
            "disk_total_gb": round(disk.total / 1024**3, 1),
            "disk_percent": round(disk.used / disk.total * 100, 1)
        },
        "services": {
            "backend": True,
            "sms_gateway": sms_ok,
            "cameras_active": len([c for c in camera_status.get("cameras", []) if c.get("status") == "running"]),
            "cameras_total": total_cameras
        }
    }

@app.post("/admin/set-plan")
def admin_set_plan(data: dict, db: Session = Depends(get_db)):
    if data.get("password") != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(UserDB).filter(UserDB.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.plan = data.get("plan")
    db.commit()
    return {"ok": True}

