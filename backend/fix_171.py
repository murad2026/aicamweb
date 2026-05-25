import sqlite3
conn = sqlite3.connect('ai-any-camera.db')
conn.execute("UPDATE cameras SET rtsp_url='rtsp://admin:Mered123$@192.168.3.171:554/Streaming/Channels/101' WHERE id=2")
conn.commit()
conn.close()
print('Done')
