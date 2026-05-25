import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')
rows = conn.execute("SELECT id, name, rtsp_url FROM cameras WHERE brand='axis'").fetchall()
for r in rows:
    print(r)
conn.close()
