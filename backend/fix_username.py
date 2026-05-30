content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
old = '''    verify_token = secrets.token_urlsafe(32)
    user = UserDB(email=req.email, username=req.username, hashed_password=hash_password(req.password), verify_token=verify_token, is_verified=0)'''
new = '''    verify_token = secrets.token_urlsafe(32)
    import re
    base_username = re.sub(r'[^a-z0-9]', '', req.email.split('@')[0].lower()) or 'user'
    username = base_username
    suffix = 1
    while db.query(UserDB).filter(UserDB.username == username).first():
        username = f"{base_username}{suffix}"
        suffix += 1
    user = UserDB(email=req.email, username=username, hashed_password=hash_password(req.password), verify_token=verify_token, is_verified=0)'''
content = content.replace(old, new)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
