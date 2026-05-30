content = open("C:/aianycam/backend/email_service.py", encoding="utf-8").read()
content = content.replace(
    'verify_url = f"https://b48a-108-26-229-43.ngrok-free.app/auth/verify/{token}"',
    'verify_url = f"https://aianycamera.com?token={token}"'
)
content = content.replace(
    'reset_url = f"https://49ea-108-26-229-43.ngrok-free.app/reset-password?token={token}"',
    'reset_url = f"https://aianycamera.com?token={token}"'
)
open("C:/aianycam/backend/email_service.py", "w", encoding="utf-8").write(content)
print("Done")
