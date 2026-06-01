content = open("C:/aianycam/backend/photo_service.py", encoding="utf-8").read()
content = content.replace(
    "public_id=f\"{camera_name}_{int(__import__('time').time())}\",",
    "public_id=f\"{camera_name}_{int(__import__('time').time())}_{__import__('random').randint(1000,9999)}\","
)
open("C:/aianycam/backend/photo_service.py", "w", encoding="utf-8").write(content)
print("Done")
