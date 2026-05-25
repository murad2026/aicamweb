content = open('main.py', 'r', encoding='utf-8').read()

new_routes = '''
import random

@app.post("/auth/send-phone-verify")
def send_phone_verify(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    phone = data.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="Phone required")
    code = str(random.randint(100000, 999999))
    from datetime import datetime
    db.execute = None
    # Save code to DB
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    conn.execute("DELETE FROM phone_verify_codes WHERE user_id=?", (current_user.id,))
    conn.execute("INSERT INTO phone_verify_codes (user_id, phone, code, created_at) VALUES (?,?,?,?)",
                 (current_user.id, phone, code, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    # Send SMS
    from sms_service import send_sms
    send_sms(phone, f"Your AI Any Camera verification code: {code}")
    return {"ok": True}

@app.post("/auth/verify-phone")
def verify_phone(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    code = data.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code required")
    import sqlite3
    conn = sqlite3.connect("C:/aianycam/backend/ai-any-camera.db")
    row = conn.execute("SELECT phone, code, created_at FROM phone_verify_codes WHERE user_id=? ORDER BY id DESC LIMIT 1",
                       (current_user.id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=400, detail="No verification code found")
    from datetime import datetime
    created = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - created).seconds > 600:
        raise HTTPException(status_code=400, detail="Code expired")
    if row[1] != code:
        raise HTTPException(status_code=400, detail="Invalid code")
    # Save phone and mark verified
    current_user.phone = row[0]
    current_user.phone_verified = 1
    db.commit()
    return {"ok": True, "phone": row[0]}
'''

# Insert before delete-account route
content = content.replace('@app.delete("/auth/delete-account")', new_routes + '\n@app.delete("/auth/delete-account")')
open('main.py', 'w', encoding='utf-8').write(content)
print('Done')
