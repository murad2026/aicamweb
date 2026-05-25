import sqlite3
conn = sqlite3.connect('ai-any-camera.db')
conn.execute('ALTER TABLE users ADD COLUMN phone TEXT')
conn.commit()
conn.close()
print('Done')
