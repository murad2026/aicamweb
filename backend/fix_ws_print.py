content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    '''    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            # Handle snapshot response
            if msg.get("type") == "snapshot":''',
    '''    try:
        print(f"🔄 Waiting for frames: camera {camera_id}", flush=True)
        while True:
            data = await websocket.receive_text()
            print(f"📨 Got message type: {json.loads(data).get('type')}", flush=True)
            msg = json.loads(data)

            # Handle snapshot response
            if msg.get("type") == "snapshot":'''
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
