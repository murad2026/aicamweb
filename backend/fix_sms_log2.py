content = open("C:/aianycam/backend/sms_service.py", encoding="utf-8").read()
content = content.replace(
    "        r = requests.post(",
    "        print(f'SENDING SMS: {message[:100]}', flush=True)\n        r = requests.post("
)
open("C:/aianycam/backend/sms_service.py", "w", encoding="utf-8").write(content)
print("Done")
