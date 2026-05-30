content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

old = '''@app.websocket("/ws/tunnel/{camera_id}")
async def camera_tunnel(websocket: WebSocket, camera_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    
    # Verify token
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001)
            return
        from auth import get_current_user_by_token
        user = get_current_user_by_token(token, db)
        if not user:
            await websocket.close(code=4001)
            return
        
        cam = db.query(CameraDB).filter(CameraDB.id == camera_id, CameraDB.user_id == user.id).first()
        if not cam:
            await websocket.close(code=4004)
            return
    except Exception as e:
        print(f"WS auth error: {e}")
        await websocket.close(code=4001)
        return'''

new = '''@app.websocket("/ws/tunnel/{camera_id}")
async def camera_tunnel(websocket: WebSocket, camera_id: int):
    await websocket.accept()
    
    # Verify token
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001)
            return
        from auth import get_current_user_by_token
        from database import SessionLocal
        db = SessionLocal()
        user = get_current_user_by_token(token, db)
        if not user:
            db.close()
            await websocket.close(code=4001)
            return
        
        cam = db.query(CameraDB).filter(CameraDB.id == camera_id, CameraDB.user_id == user.id).first()
        if not cam:
            db.close()
            await websocket.close(code=4004)
            return
        db.close()
    except Exception as e:
        print(f"WS auth error: {e}")
        import traceback; traceback.print_exc()
        await websocket.close(code=4001)
        return'''

content = content.replace(old, new)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done" if old in open("C:/aianycam/backend/main.py", encoding="utf-8").read() == False else "Not found - check manually")
