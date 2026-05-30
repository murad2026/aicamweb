content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
# Remove from line 793
content = content.replace(
    "\ntunnel_snapshots = {}  # camera_id -> base64 jpeg",
    ""
)
# Add near top after active_tunnels
content = content.replace(
    "active_tunnels = {}  # camera_id -> websocket",
    "active_tunnels = {}  # camera_id -> websocket\ntunnel_snapshots = {}  # camera_id -> base64 jpeg"
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
