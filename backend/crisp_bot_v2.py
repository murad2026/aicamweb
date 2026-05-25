"""
Crisp polling bot - runs alongside uvicorn
Checks for new messages every 4 seconds and responds with Claude AI
"""
import time
import requests

CRISP_WEBSITE_ID = "4d8501f9-ee54-4f41-8f91-e69937105b82"
CRISP_API_ID = "fa97793d-1fdb-44a2-931b-e416d55f3aeb"
CRISP_API_KEY = "0b78f41d0dfb019dfd19682b709cadd9b83c51cc0e481fed3f72410ef934f457"
ANTHROPIC_KEY = "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"
OWNER_PHONE = "+16173724119"

CRISP_SYSTEM = """You are an AI assistant for AI Any Camera — a smart security camera monitoring platform.
You help users with connecting cameras, setting up alerts, and understanding plans.
Plans: Free (1 camera), Pro $19/mo (5 cameras), Premium $49/mo (unlimited + AI subject recognition), Enterprise (40+ cameras, custom pricing, remote setup services).
Be concise, friendly and helpful. Answer in the same language the user writes in.
Keep responses short — max 3-4 sentences."""

HUMAN_KEYWORDS = ["talk to human", "real person", "live agent", "human agent", "speak with someone",
                  "talk to agent", "enterprise", "custom quote", "contact sales", "agent", "human",
                  "speak to", "call me", "representative"]

auth = (CRISP_API_ID, CRISP_API_KEY)
headers = {"X-Crisp-Tier": "user"}

sessions = {}

def get_conversations():
    try:
        r = requests.get(
            f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/1",
            auth=auth, headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json().get("data", [])
    except Exception as e:
        print(f"Get conversations error: {e}")
    return []

def get_messages(session_id):
    try:
        r = requests.get(
            f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/messages",
            auth=auth, headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json().get("data", [])
    except Exception as e:
        print(f"Get messages error: {e}")
    return []

def send_message(session_id, content):
    try:
        r = requests.post(
            f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/message",
            auth=auth, headers=headers, timeout=10,
            json={"type": "text", "content": content, "from": "operator", "origin": "chat"}
        )
        return r.status_code == 200
    except Exception as e:
        print(f"Send message error: {e}")
    return False

def send_picker(session_id, text, choices):
    try:
        r = requests.post(
            f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/message",
            auth=auth, headers=headers, timeout=10,
            json={
                "type": "picker",
                "from": "operator",
                "origin": "chat",
                "content": {
                    "id": "picker_" + str(int(time.time())),
                    "text": text,
                    "choices": choices
                }
            }
        )
        return r.status_code == 200
    except Exception as e:
        print(f"Send picker error: {e}")
    return False

def set_pending(session_id):
    try:
        requests.patch(
            f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/state",
            auth=auth, headers=headers, timeout=10,
            json={"state": "pending"}
        )
    except Exception as e:
        print(f"Set pending error: {e}")

def send_sms_alert(message):
    try:
        from sms_service import send_sms
        send_sms(OWNER_PHONE, message)
    except Exception as e:
        print(f"SMS error: {e}")

def get_ai_reply(messages_history, last_user_message):
    try:
        ai_messages = []
        for m in messages_history[-10:]:
            content = m.get("content", "")
            if isinstance(content, dict):
                content = content.get("text", str(content))
            content = str(content).strip()
            if not content:
                continue
            if m.get("from") == "user":
                ai_messages.append({"role": "user", "content": content})
            elif m.get("from") in ("operator", "bot"):
                ai_messages.append({"role": "assistant", "content": content})

        if not ai_messages:
            ai_messages = [{"role": "user", "content": last_user_message}]

        # Ensure alternating roles
        cleaned = []
        for msg in ai_messages:
            if cleaned and cleaned[-1]["role"] == msg["role"]:
                cleaned[-1]["content"] += "\n" + msg["content"]
            else:
                cleaned.append(msg)

        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 400, "system": CRISP_SYSTEM, "messages": cleaned},
            timeout=30
        )
        result = r.json()
        return result.get("content", [{}])[0].get("text", "")
    except Exception as e:
        print(f"Claude API error: {e}")
    return ""

def escalate(session_id, last_message):
    send_message(session_id, "I'm connecting you with our team right now! 🙋 You'll hear from us shortly.")
    set_pending(session_id)
    send_sms_alert(f"AI Any Camera LEAD: User wants human. Message: {last_message[:100]}")
    print(f"Escalated {session_id}")

def poll_loop():
    print("Crisp bot polling started (4s interval)")
    while True:
        try:
            conversations = get_conversations()
            for conv in conversations:
                session_id = conv.get("session_id")
                if not session_id:
                    continue

                if session_id not in sessions:
                    sessions[session_id] = {"last_msg_id": None, "greeted": False, "escalated": False, "offered_human": False}

                sess = sessions[session_id]
                if sess["escalated"]:
                    continue

                messages = get_messages(session_id)
                if not messages:
                    continue

                # Find last user message
                last_user_msg = None
                last_user_ts = 0
                last_msg_id = None

                for m in reversed(messages):
                    if m.get("from") == "user":
                        content = m.get("content", "")
                        if isinstance(content, dict):
                            sel = content.get("selected", {})
                            last_user_msg = sel.get("value", str(content)) if isinstance(sel, dict) else str(content)
                        elif content:
                            last_user_msg = str(content)
                        last_user_ts = m.get("timestamp", 0)
                        last_msg_id = m.get("fingerprint") or last_user_ts
                        break

                if not last_user_msg:
                    continue

                if sess["last_msg_id"] == last_msg_id:
                    continue

                # Skip if operator already replied last
                last_msg = messages[-1] if messages else {}
                if last_msg.get("from") in ("operator", "bot"):
                    sess["last_msg_id"] = last_msg_id
                    continue

                # Only recent messages (10 min)
                if time.time() * 1000 - last_user_ts > 600000:
                    sess["last_msg_id"] = last_msg_id
                    continue

                print(f"User [{session_id[:8]}]: {last_user_msg[:60]}")

                # Check for human request
                wants_human = (
                    last_user_msg == "talk_to_human" or
                    any(kw in last_user_msg.lower() for kw in HUMAN_KEYWORDS)
                )

                if wants_human:
                    escalate(session_id, last_user_msg)
                    sess["last_msg_id"] = last_msg_id
                    sess["escalated"] = True
                    continue

                # First greeting with buttons
                if not sess["greeted"]:
                    ok = send_picker(
                        session_id,
                        "Hi! I'm the AI Any Camera assistant. What do you need help with?",
                        [
                            {"icon": "📷", "label": "Connect a camera", "value": "connect_camera", "description": "IP, DVR/NVR setup"},
                            {"icon": "💰", "label": "Pricing & Plans", "value": "pricing", "description": "Free, Pro, Premium, Enterprise"},
                            {"icon": "🚨", "label": "Set up alerts", "value": "alerts", "description": "SMS, Telegram, Email"},
                            {"icon": "👤", "label": "Talk to Human", "value": "talk_to_human", "description": "Connect with our team"},
                        ]
                    )
                    if ok:
                        sess["greeted"] = True
                        sess["last_msg_id"] = last_msg_id
                        continue

                # AI reply
                reply = get_ai_reply(messages, last_user_msg)
                if reply:
                    if send_message(session_id, reply):
                        print(f"Bot replied [{session_id[:8]}]")
                        sess["last_msg_id"] = last_msg_id
                        # Offer human button after 2nd user message
                        user_count = sum(1 for m in messages if m.get("from") == "user")
                        if user_count >= 2 and not sess["offered_human"]:
                            time.sleep(1)
                            send_picker(
                                session_id,
                                "Still need help?",
                                [{"icon": "👤", "label": "Talk to Human", "value": "talk_to_human", "description": "Connect with our team"}]
                            )
                            sess["offered_human"] = True

        except Exception as e:
            print(f"Poll error: {e}")
            import traceback; traceback.print_exc()

        time.sleep(4)

if __name__ == "__main__":
    poll_loop()
