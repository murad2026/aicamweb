content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
old = '''    verify_token = secrets.token_urlsafe(32)
    user = UserDB(email=req.email, username=req.username, hashed_password=hash_password(req.password), verify_token=verify_token, is_verified=0)
    db.add(user)
    db.commit()
    db.refresh(user)
    send_verification_email(user.email, user.username, verify_token)
    return {"message": "Check your email to verify your account"}'''
new = '''    verify_token = secrets.token_urlsafe(32)
    user = UserDB(email=req.email, username=req.username, hashed_password=hash_password(req.password), verify_token=verify_token, is_verified=0)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        if "username" in str(e):
            raise HTTPException(status_code=400, detail="Username already taken")
        if "email" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=400, detail="Registration failed")
    send_verification_email(user.email, user.username, verify_token)
    return {"message": "Check your email to verify your account"}'''
content = content.replace(old, new)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
