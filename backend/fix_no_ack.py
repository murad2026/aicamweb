content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    '            detection_queue.put_nowait((camera_id, frame.copy()))\n            await websocket.send_text(json.dumps({"type": "ack"}))',
    '            try:\n                detection_queue.put_nowait((camera_id, frame.copy()))\n            except:\n                pass  # Queue full, skip frame'
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
