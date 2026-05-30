content = open("C:/aianycam/backend/email_service.py", encoding="utf-8").read()
content = content.replace(
    'verify_url = f"https://aianycamera.com?token={token}"',
    'verify_url = f"https://aianycamera.com?verify={token}"'
)
open("C:/aianycam/backend/email_service.py", "w", encoding="utf-8").write(content)
print("Done")
