import sqlite3
c = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
c.execute("DELETE FROM subjects")
c.execute("DELETE FROM subject_sightings")
c.commit()
c.close()
print("Cleared")
