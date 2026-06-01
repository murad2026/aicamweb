content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

# 1. Add request_snapshot endpoint
new_endpoint = '''
@app.get("/cameras/{cam_id}/request_snapshot")
async def request_snapshot(cam_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Ask agent to send a snapshot"""
    ws = active_tunnels.get(cam_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Camera agent not connected")
    await ws.send_text(json.dumps({"type": "get_snapshot"}))
    return {"ok": True, "eta_seconds": 3}

'''

# Insert before GET snapshot
content = content.replace(
    '@app.get("/cameras/{cam_id}/snapshot")',
    new_endpoint + '@app.get("/cameras/{cam_id}/snapshot")'
)

# 2. Change WebSocket to handle snapshot requests and motion-only frames
old_ws_loop = '''    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") != "frame":
                continue'''

new_ws_loop = '''    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            # Handle snapshot response
            if msg.get("type") == "snapshot":
                frame_bytes = base64.b64decode(msg["frame"])
                tunnel_snapshots[camera_id] = msg["frame"]
                print(f"📸 Snapshot received: {cam.name}")
                continue

            if msg.get("type") != "frame":
                continue'''

content = content.replace(old_ws_loop, new_ws_loop)

open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
