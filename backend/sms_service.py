import requests, time
SMS_SERVER_URL = "https://sms.aianycamera.com/send-sms"
API_KEY = "AiAnyCam2026"
last_sms = {}
COOLDOWN = 60

def send_sms(phone, message):
    now = time.time()
    if now - last_sms.get(phone, 0) < COOLDOWN:
        print("SMS cooldown, skipping")
        return False
    last_sms[phone] = now
    try:
        r = requests.post(SMS_SERVER_URL, json={"api_key": API_KEY, "phone": phone, "message": message}, timeout=15)
        print(f"SMS sent: {r.status_code} {r.text}")
        return r.json().get("success", False)
    except Exception as e:
        print(f"SMS error: {e}")
        return False
