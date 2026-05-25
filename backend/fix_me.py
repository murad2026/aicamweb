with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''@app.get("/auth/me")
def me(current_user: UserDB = Depends(get_current_user)):'''

new = '''@app.get("/auth/me")
def me(current_user: UserDB = Depends(get_current_user)):
    plan = getattr(current_user, "plan", "free") or "free"
    cam_count = 0
    try:
        from database import SessionLocal
        db = SessionLocal()
        cam_count = db.query(CameraDB).filter(CameraDB.user_id == current_user.id).count()
        db.close()
    except: pass
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "is_verified": current_user.is_verified,
        "telegram_chat_id": current_user.telegram_chat_id,
        "phone": current_user.phone,
        "phone_verified": getattr(current_user, "phone_verified", 0),
        "plan": plan,
        "cam_count": cam_count
    }

@app.post("/auth/upgrade")
def upgrade_plan(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    plan = data.get("plan")
    if plan not in ["pro", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid plan")
    current_user.plan = plan
    db.commit()
    return {"ok": True, "plan": plan}

@app.get("/auth/me")
def me_old(current_user: UserDB = Depends(get_current_user)):'''

content = content.replace(old, new)
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
