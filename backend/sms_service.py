import requests

SMS_SERVER_URL = "https://negotiation-translated-attempted-appendix.trycloudflare.com/send-sms"
API_KEY = "AiAnyCam2026!"

def send_sms(phone, message):
    try:
        r = requests.post(SMS_SERVER_URL, json={"api_key": API_KEY, "phone": phone, "message": message}, timeout=15)
        print(f"SMS sent: {r.status_code} {r.text}")
        return r.json().get("success", False)
    except Exception as e:
        print(f"SMS error: {e}")
        return False
