import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')
try:
    conn.execute("ALTER TABLE events ADD COLUMN viewed INTEGER DEFAULT 0")
    print('Added viewed column')
except:
    print('Already exists')
conn.commit()
conn.close()
