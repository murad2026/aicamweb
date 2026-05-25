with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_routes = '''
@app.get("/subjects")
def get_subjects(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    rows = conn.execute("SELECT id, name, class, photo_url, first_seen, last_seen, seen_count, camera_id FROM subjects WHERE user_id=? ORDER BY last_seen DESC", (current_user.id,)).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "class": r[2], "photo_url": r[3], "first_seen": r[4], "last_seen": r[5], "seen_count": r[6], "camera_id": r[7]} for r in rows]

@app.put("/subjects/{subject_id}")
def update_subject(subject_id: int, data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("UPDATE subjects SET name=? WHERE id=? AND user_id=?", (data.get("name"), subject_id, current_user.id))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("DELETE FROM subjects WHERE id=? AND user_id=?", (subject_id, current_user.id))
    conn.commit()
    conn.close()
    return {"ok": True}
'''

content = content.replace('@app.delete("/auth/delete-account")', new_routes + '\n@app.delete("/auth/delete-account")')
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
