from sms_service import send_sms
import requests
import base64

SINCH_KEY_ID = "25954eae-e03e-4fbf-aa0f-801614b0d98d"
SINCH_KEY_SECRET = "jEctR_Vlg~.Xf-lJzxlxYHlfiS"
SINCH_PROJECT_ID = "e7023b6c-bb23-4fb3-abf5-7f820630bab9"

token = base64.b64encode(f"{SINCH_KEY_ID}:{SINCH_KEY_SECRET}".encode()).decode()
r = requests.get(f"https://US.conversation.api.sinch.com/v1/projects/{SINCH_PROJECT_ID}/apps", headers={"Authorization": f"Basic {token}"})
print(r.status_code, r.text)
