import requests
import base64

SINCH_KEY_ID = "25954eae-e03e-4fbf-aa6f-801614b0d98d"
SINCH_KEY_SECRET = "jEctR_Vlg~.Xf-1Jzx1xYHlfiS"
SINCH_PROJECT_ID = "e7023b6c-bb23-4fb3-abf5-7f820630bab9"
SINCH_APP_ID = "01KSBD0XFF3MKCYM4RDHTF2QXH"
SINCH_SENDER = "+12066578456"

def send_sms(phone, message):
    try:
        url = f"https://US.conversation.api.sinch.com/v1/projects/{SINCH_PROJECT_ID}/messages:send"
        payload = {
            "app_id": SINCH_APP_ID,
            "recipient": {
                "identified_by": {
                    "channel_identities": [{"channel": "SMS", "identity": phone}]
                }
            },
            "message": {"text_message": {"text": message}},
            "channel_properties": {"SMS_SENDER": SINCH_SENDER}
        }
        token = base64.b64encode(f"{SINCH_KEY_ID}:{SINCH_KEY_SECRET}".encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {token}"
        }
        r = requests.post(url, json=payload, headers=headers)
        print(f"SMS sent: {r.status_code} {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"SMS error: {e}")
        return False
