with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add new_subjects count to /auth/me
old = '        "plan": plan,\n        "cam_count": cam_count\n    }'
new = '        "plan": plan,\n        "cam_count": cam_count,\n        "new_subjects": __import__("sqlite3").connect("C:/aianycam/backend/ai-any-camera.db").execute("SELECT COUNT(*) FROM subjects WHERE user_id=? AND viewed=0", (current_user.id,)).fetchone()[0] if plan == "premium" else 0\n    }'

content = content.replace(old, new)

# Add mark as viewed route
new_route = '''
@app.post("/subjects/mark-viewed")
def mark_subjects_viewed(current_user = Depends(get_current_user)):
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("UPDATE subjects SET viewed=1 WHERE user_id=?", (current_user.id,))
    conn.commit()
    conn.close()
    return {"ok": True}
'''

content = content.replace('@app.delete("/subjects/', new_route + '\n@app.delete("/subjects/')
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
