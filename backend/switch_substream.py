import sqlite3

conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
cameras = conn.execute("SELECT id, name, rtsp_url, brand FROM cameras").fetchall()

updated = 0
for cam_id, name, rtsp_url, brand in cameras:
    new_url = rtsp_url
    
    # Hikvision: channel 101 -> 102 (substream)
    if "/Streaming/Channels/101" in rtsp_url:
        new_url = rtsp_url.replace("/Streaming/Channels/101", "/Streaming/Channels/102")
    
    # Dahua DVR/NVR: subtype=0 -> subtype=1
    elif "subtype=0" in rtsp_url:
        new_url = rtsp_url.replace("subtype=0", "subtype=1")
    
    # Axis: add resolution parameter
    elif "axis-media" in rtsp_url and "resolution" not in rtsp_url:
        if "?" in rtsp_url:
            new_url = rtsp_url + "&resolution=640x480"
        else:
            new_url = rtsp_url + "?resolution=640x480"
    
    if new_url != rtsp_url:
        conn.execute("UPDATE cameras SET rtsp_url=? WHERE id=?", (new_url, cam_id))
        print(f"✅ {name}: substream enabled")
        updated += 1
    else:
        print(f"⏭ {name}: no change ({brand})")

conn.commit()
conn.close()
print(f"\nDone! Updated {updated} cameras.")
