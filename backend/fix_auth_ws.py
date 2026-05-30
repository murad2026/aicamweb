content = open("C:/aianycam/backend/auth.py", encoding="utf-8").read()
content += '''

def get_current_user_by_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.query(UserDB).filter(UserDB.id == int(user_id)).first()
    except:
        return None
'''
open("C:/aianycam/backend/auth.py", "w", encoding="utf-8").write(content)
print("Done")
