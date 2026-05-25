import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')
conn.execute("UPDATE cameras SET brand='dahua' WHERE id=15")
conn.commit()
conn.close()
print('Done')
