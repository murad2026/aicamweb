import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')

# Get user_id from existing camera
user_id = conn.execute("SELECT user_id FROM cameras LIMIT 1").fetchone()[0]

cameras = [
    # Hikvision
    ("Camera 192.168.3.105", "rtsp://admin:Mered123$@192.168.3.105:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.198", "rtsp://admin:Mered123$@192.168.3.198:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.171", "rtsp://admin:Mered123$@192.168.3.171:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.101", "rtsp://admin:Mered123$@192.168.3.101:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.130", "rtsp://admin:Mered123$@192.168.3.130:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.8",   "rtsp://admin:Mered123$@192.168.3.8:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.29",  "rtsp://admin:Mered123$@192.168.3.29:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.43",  "rtsp://admin:Mered123$@192.168.3.43:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.76",  "rtsp://admin:Mered123$@192.168.3.76:554/Streaming/Channels/101", "hikvision"),
    ("Camera 192.168.3.142", "rtsp://admin:Mered123$@192.168.3.142:554/Streaming/Channels/101", "hikvision"),
    # Axis
    ("Camera 192.168.3.196", "rtsp://admin:Mered123$@192.168.3.196/axis-media/media.amp", "axis"),
    ("Camera 192.168.3.215", "rtsp://admin:Mered123$@192.168.3.215/axis-media/media.amp", "axis"),
    ("Camera 192.168.3.77",  "rtsp://admin:Mered123$@192.168.3.77/axis-media/media.amp", "axis"),
]

for name, rtsp, brand in cameras:
    try:
        conn.execute(
            "INSERT INTO cameras (user_id, name, rtsp_url, brand, detect_classes) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, rtsp, brand, '["person"]')
        )
        print(f"Added: {name}")
    except Exception as e:
        print(f"Skip {name}: {e}")

conn.commit()
conn.close()
print("Done")
