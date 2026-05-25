# Добавить эти роуты в main.py ПЕРЕД строкой "# Serve frontend"

@app.get("/subjects/{subject_id}/sightings")
def get_subject_sightings(subject_id: int, current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    # Verify subject belongs to user
    owner = conn.execute("SELECT user_id FROM subjects WHERE id=?", (subject_id,)).fetchone()
    if not owner or owner[0] != current_user.id:
        conn.close()
        raise HTTPException(status_code=404, detail="Not found")
    rows = conn.execute(
        "SELECT id, camera_id, camera_name, timestamp, photo_url FROM subject_sightings WHERE subject_id=? ORDER BY timestamp DESC LIMIT 50",
        (subject_id,)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "camera_id": r[1], "camera_name": r[2], "timestamp": r[3], "photo_url": r[4]} for r in rows]


@app.get("/recognized")
def get_recognized(current_user = Depends(get_current_user)):
    """Subjects seen more than once (recurring = truly recognized by AI)"""
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    rows = conn.execute(
        "SELECT id, name, class, photo_url, first_seen, last_seen, seen_count, camera_id FROM subjects WHERE user_id=? AND seen_count > 1 ORDER BY last_seen DESC",
        (current_user.id,)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "class": r[2], "photo_url": r[3], "first_seen": r[4], "last_seen": r[5], "seen_count": r[6], "camera_id": r[7]} for r in rows]
