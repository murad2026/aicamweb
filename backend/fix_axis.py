import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')
for ip in ['192.168.3.196', '192.168.3.215', '192.168.3.77']:
    url = f'rtsp://root:Mered123$@{ip}/axis-media/media.amp?videocodec=h264'
    conn.execute(f"UPDATE cameras SET rtsp_url=? WHERE name=?", (url, f'Camera {ip}'))
    print(f'Updated: {ip}')
conn.commit()
conn.close()
print('Done')
