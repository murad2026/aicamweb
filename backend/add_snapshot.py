content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

new_code = '''
@app.post("/cameras/{cam_id}/snapshot")
async def post_snapshot(cam_id: int, request: Request, db: Session = Depends(get_db)):
    """Receive snapshot from agent tunnel"""
    data = await request.json()
    image_b64 = data.get("image")
    if not image_b64:
        raise HTTPException(status_code=400, detail="No image")
    # Store in memory
    tunnel_snapshots[cam_id] = image_b64
    return {"ok": True}

'''

# Add storage dict near top
content = content.replace(
    "active_tunnels = {}  # camera_id -> websocket",
    "active_tunnels = {}  # camera_id -> websocket\ntunnel_snapshots = {}  # camera_id -> base64 jpeg"
)

# Add POST snapshot route before GET snapshot
content = content.replace(
    "@app.get(\"/cameras/{cam_id}/snapshot\")",
    new_code + "@app.get(\"/cameras/{cam_id}/snapshot\")"
)

# Modify GET snapshot to check tunnel_snapshots first
content = content.replace(
    "    worker = workers.get(cam.id)\n    if worker and worker.last_frame is not None:",
    "    # Check tunnel snapshot first\n    if cam.id in tunnel_snapshots:\n        return {\"image\": f\"data:image/jpeg;base64,{tunnel_snapshots[cam.id]}\"}\n    worker = workers.get(cam.id)\n    if worker and worker.last_frame is not None:"
)

open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
