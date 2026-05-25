import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')
try:
    conn.execute('ALTER TABLE events ADD COLUMN telegram_message_id TEXT')
except: pass
try:
    conn.execute('ALTER TABLE events ADD COLUMN telegram_chat_id TEXT')
except: pass
conn.commit()
conn.close()
print('Done')
