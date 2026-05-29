import sqlite3

conn = sqlite3.connect("ai-any-camera.db")
cameras = conn.execute("SELECT id, name, rtsp_url, brand FROM cameras").fetchall()

updated = 0
for cam_id, name, rtsp_url, brand in cameras:
    new_url = rtsp_url

    if "/Streaming/Channels/101" in rtsp_url:
        new_url = rtsp_url.replace("/Streaming/Channels/101", "/Streaming/Channels/102")
    elif "subtype=0" in rtsp_url:
        new_url = rtsp_url.replace("subtype=0", "subtype=1")
    elif "axis-media" in rtsp_url and "resolution" not in rtsp_url:
        new_url = rtsp_url + ("&" if "?" in rtsp_url else "?") + "resolution=640x480"

    if new_url != rtsp_url:
        conn.execute("UPDATE cameras SET rtsp_url=? WHERE id=?", (new_url, cam_id))
        print("Updated:", name)
        updated += 1
    else:
        print("Skip:", name, brand)

conn.commit()
conn.close()
print("Done! Updated", updated, "cameras")
