import sqlite3
conn = sqlite3.connect('ai-any-camera.db')
url = 'rtsp://root:Mered123$@192.168.3.171:554/Streaming/Channels/101'
conn.execute("INSERT INTO cameras (user_id, name, rtsp_url, brand, detect_classes) VALUES (3, 'Camera 171', ?, 'hikvision', '[\"person\"]')", (url,))
conn.commit()
conn.close()
print('Done')
