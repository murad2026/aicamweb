import sqlite3
conn = sqlite3.connect('ai-any-camera.db')
rows = conn.execute("SELECT id, name, rtsp_url FROM cameras").fetchall()
for r in rows:
    print(r)
conn.close()
