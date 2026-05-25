import requests

SMS_GATEWAY_URL = "http://192.168.2.6:8080/send-sms"

def send_sms(phone, message):
    try:
        r = requests.post(
            SMS_GATEWAY_URL,
            json={"phone": phone, "message": message},
            timeout=10
        )
        result = r.json()
        print(f"SMS sent: {r.status_code} {r.text}")
        return result.get("success", False)
    except Exception as e:
        print(f"SMS error: {e}")
        return False
