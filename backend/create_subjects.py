import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')
conn.execute("""CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    camera_id INTEGER,
    name TEXT,
    class TEXT,
    photo_url TEXT,
    first_seen TEXT,
    last_seen TEXT,
    seen_count INTEGER DEFAULT 1
)""")
conn.commit()
conn.close()
print('Done')
