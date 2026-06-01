content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "            send_sms(cam.notify_sms, msg)",
    "            print(f'SMS MESSAGE: {msg}', flush=True)\n            send_sms(cam.notify_sms, msg)"
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
