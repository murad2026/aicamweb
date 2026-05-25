"""
Crisp polling bot - runs alongside uvicorn
Checks for new messages every 10 seconds and responds with Claude AI
"""
import time
import requests
import threading

CRISP_WEBSITE_ID = "4d8501f9-ee54-4f41-8f91-e69937105b82"
CRISP_API_ID = "40a0a408-28f0-4ee5-8963-04b9e2e88e18"
CRISP_API_KEY = "66deb146a06d8cd2b2d30c22770a973a80292b85f1c3571a5685c77508bec30e"
ANTHROPIC_KEY = "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"
OWNER_PHONE = "+16173724119"

CRISP_SYSTEM = """You are an AI assistant for AI Any Camera — a smart security camera monitoring platform.
You help users with connecting cameras, setting up alerts, and understanding plans.
Plans: Free (1 camera), Pro $19/mo (5 cameras), Premium $49/mo (unlimited + AI subject recognition), Enterprise (40+ cameras, custom pricing, remote setup services).
When users want Enterprise or want to talk to a human — tell them you're notifying the team and they'll be in touch shortly.
Be concise, friendly and helpful. Answer in the same language the user writes in."""

HUMAN_KEYWORDS = ["talk to human", "real person", "live agent", "human agent", "speak with someone",
                  "talk to agent", "enterprise", "custom quote", "contact sales", "agent", "human"]

auth = (CRISP_API_ID, CRISP_API_KEY)
headers = {"X-Crisp-Tier": "plugin"}

# Track which sessions we already responded to (session_id -> last_message_id)
responded = {}

def get_conversations():
    """Get list of open conversations."""
    try:
        r = requests.get(
            f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversations/1",
            auth=auth, headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json().get("data", [])
    except Exception as e:
        print(f"Crisp get conversations error: {e}")
    return []

def get_messages(session_id):
    """Get messages for a conversation."""
    try:
        r = requests.get(
            f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/messages",
            auth=auth, headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json().get("data", [])
    except Exception as e:
        print(f"Crisp get messages error: {e}")
    return []

def send_message(session_id, content):
    """Send a message to a conversation."""
    try:
        r = requests.post(
            f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/message",
            auth=auth, headers=headers, timeout=10,
            json={"type": "text", "content": content, "from": "operator", "origin": "chat"}
        )
        return r.status_code == 200
    except Exception as e:
        print(f"Crisp send message error: {e}")
    return False

def get_ai_reply(messages_history, last_user_message):
    """Get Claude AI reply."""
    try:
        # Build message history for Claude
        ai_messages = []
        for m in messages_history[-10:]:
            if m.get("from") == "user" and m.get("content"):
                ai_messages.append({"role": "user", "content": str(m["content"])})
            elif m.get("from") in ("operator", "bot") and m.get("content"):
                ai_messages.append({"role": "assistant", "content": str(m["content"])})

        if not ai_messages:
            ai_messages = [{"role": "user", "content": last_user_message}]

        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 400,
                "system": CRISP_SYSTEM,
                "messages": ai_messages
            },
            timeout=30
        )
        result = r.json()
        return result.get("content", [{}])[0].get("text", "")
    except Exception as e:
        print(f"Claude API error: {e}")
    return ""

def send_sms_alert(message):
    """Send SMS to owner."""
    try:
        from sms_service import send_sms
        send_sms(OWNER_PHONE, message)
    except Exception as e:
        print(f"SMS error: {e}")

def poll_loop():
    """Main polling loop."""
    print("🤖 Crisp bot polling started")
    while True:
        try:
            conversations = get_conversations()
            for conv in conversations:
                session_id = conv.get("session_id")
                if not session_id:
                    continue

                messages = get_messages(session_id)
                if not messages:
                    continue

                # Find last user message
                last_user_msg = None
                last_user_ts = 0
                last_msg_id = None

                for m in reversed(messages):
                    if m.get("from") == "user" and m.get("content"):
                        last_user_msg = str(m["content"])
                        last_user_ts = m.get("timestamp", 0)
                        last_msg_id = m.get("fingerprint") or last_user_ts
                        break

                if not last_user_msg:
                    continue

                # Check if we already responded to this message
                if responded.get(session_id) == last_msg_id:
                    continue

                # Check if last message is from operator (already responded)
                last_msg = messages[-1] if messages else {}
                if last_msg.get("from") in ("operator", "bot"):
                    responded[session_id] = last_msg_id
                    continue

                # Check if message is recent (last 5 minutes)
                import time as t
                if t.time() * 1000 - last_user_ts > 300000:
                    responded[session_id] = last_msg_id
                    continue

                print(f"🤖 New message in {session_id}: {last_user_msg[:50]}")

                # Check if user wants human
                wants_human = any(kw in last_user_msg.lower() for kw in HUMAN_KEYWORDS)

                if wants_human:
                    reply = "I'm connecting you with our team right now! 🙋 You'll hear from us shortly."
                    send_sms_alert(f"AI Any Camera LEAD via Crisp: {last_user_msg[:100]}")
                else:
                    reply = get_ai_reply(messages, last_user_msg)

                if reply:
                    if send_message(session_id, reply):
                        print(f"✅ Replied to {session_id}")
                        responded[session_id] = last_msg_id
                    else:
                        print(f"❌ Failed to send reply to {session_id}")

        except Exception as e:
            print(f"Poll loop error: {e}")

        time.sleep(10)

if __name__ == "__main__":
    poll_loop()
