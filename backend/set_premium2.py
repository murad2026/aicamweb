import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')
conn.execute("UPDATE users SET plan='premium' WHERE username='testuser3'")
conn.commit()
conn.close()
print('Done')
