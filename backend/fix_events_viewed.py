with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_route = '''
@app.post("/events/{cam_id}/mark-viewed")
def mark_events_viewed(cam_id: int, current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("UPDATE events SET viewed=1 WHERE camera_id=?", (cam_id,))
    conn.commit()
    conn.close()
    return {"ok": True}
'''

content = content.replace('@app.delete("/auth/delete-account")', new_route + '\n@app.delete("/auth/delete-account")')
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
