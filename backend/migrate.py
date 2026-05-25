import sqlite3
conn = sqlite3.connect('C:/aianycam/backend/ai-any-camera.db')
try:
    conn.execute("ALTER TABLE users ADD COLUMN phone_verified INTEGER DEFAULT 0")
    print('Added phone_verified')
except:
    print('phone_verified already exists')
try:
    conn.execute("""CREATE TABLE IF NOT EXISTS phone_verify_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        phone TEXT NOT NULL,
        code TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    print('Created phone_verify_codes table')
except Exception as e:
    print(f'Error: {e}')
conn.commit()
conn.close()
