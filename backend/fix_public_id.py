content = open("C:/aianycam/backend/photo_service.py", encoding="utf-8").read()
content = content.replace(
    'public_id=f"{camera_name}_{int(__import__(\'time\').time())}_{__import__(\'random\').randint(1000,9999)}",\n            overwrite=True',
    'public_id=f"alert_{int(__import__(\'time\').time())}_{__import__(\'random\').randint(10000,99999)}",\n            overwrite=False,\n            invalidate=True'
)
open("C:/aianycam/backend/photo_service.py", "w", encoding="utf-8").write(content)
print("Done")
