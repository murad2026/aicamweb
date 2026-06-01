content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

# Add validation before SMS
old = '''    if cam.notify_sms:
        try:
            from sms_service import send_sms
            msg = caption
            if photo_url:
                msg += f" Photo: {photo_url}"
            print(f'SMS MESSAGE: {msg}', flush=True)
            send_sms(cam.notify_sms, msg)'''

new = '''    if cam.notify_sms:
        try:
            from sms_service import send_sms
            msg = caption
            if photo_url:
                # Validate photo is fresh (uploaded within last 60 seconds)
                import re, time
                match = re.search(r'/v(\d+)/', photo_url)
                if match:
                    photo_ts = int(match.group(1))
                    age = int(time.time()) - photo_ts
                    if age > 60:
                        print(f"Photo too old ({age}s), skipping URL")
                        photo_url = None
                if photo_url:
                    msg += f" Photo: {photo_url}"
            print(f'SMS MESSAGE: {msg}', flush=True)
            send_sms(cam.notify_sms, msg)'''

content = content.replace(old, new)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
