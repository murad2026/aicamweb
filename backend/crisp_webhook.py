import httpx

CRISP_WEBSITE_ID = "4d8501f9-ee54-4f41-8f91-e69937105b82"
CRISP_API_ID = "40a0a408-28f0-4ee5-8963-04b9e2e88e18"
CRISP_API_KEY = "66deb146a06d8cd2b2d30c22770a973a80292b85f1c3571a5685c77508bec30e"

CRISP_SYSTEM = """You are an AI assistant for AI Any Camera — a smart security camera monitoring platform. 

You help users with:
- Connecting IP cameras, DVR/NVR systems (Hikvision, Dahua, Axis, etc.)
- Setting up motion detection alerts via SMS, Telegram, Email
- Understanding plans: Free (1 camera), Pro $19/mo (5 cameras), Premium $49/mo (unlimited + AI subject recognition)
- Enterprise plans for businesses with 40+ cameras — custom pricing, remote setup services

When users ask about pricing for large deployments or want a custom quote, tell them you'll connect them with the team.
When users say "talk to human", "agent", "real person", or want to discuss Enterprise — say you're notifying the team now.
Be concise, friendly and helpful."""

HUMAN_KEYWORDS = ["talk to human", "real person", "live agent", "human agent", "speak with someone", "talk to agent", "enterprise", "custom quote", "contact sales"]

@app.post("/crisp/webhook")
async def crisp_webhook(request: Request):
    try:
        data = await request.json()
    except:
        return {"ok": True}

    event = data.get("event", "")
    if event != "message:send":
        return {"ok": True}

    msg_data = data.get("data", {})
    content = msg_data.get("content", "")
    session_id = msg_data.get("session_id", "")
    origin = msg_data.get("origin", "")

    # Only respond to user messages, not operator/bot messages
    if origin in ("operator", "bot"):
        return {"ok": True}

    if not content or not session_id:
        return {"ok": True}

    # Check if user wants human
    content_lower = content.lower()
    wants_human = any(kw in content_lower for kw in HUMAN_KEYWORDS)

    if wants_human:
        reply = "I'm connecting you with our team right now! 🙋 You'll hear from us shortly. In the meantime, feel free to share more details about your needs."
        # Send SMS to owner
        try:
            from sms_service import send_sms
            send_sms("+16173724119", f"AI Any Camera LEAD via Crisp: User wants to talk. Message: {content[:100]}")
        except Exception as e:
            print(f"SMS error: {e}")
    else:
        # Get conversation history from Crisp
        messages_for_ai = [{"role": "user", "content": content}]
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(
                    f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/messages",
                    auth=(CRISP_API_ID, CRISP_API_KEY),
                    headers={"X-Crisp-Tier": "plugin"}
                )
                if r.status_code == 200:
                    msgs = r.json().get("data", [])[-10:]  # last 10 messages
                    messages_for_ai = []
                    for m in msgs:
                        role = "assistant" if m.get("from") in ("operator", "bot") else "user"
                        if m.get("content"):
                            messages_for_ai.append({"role": role, "content": m["content"]})
        except Exception as e:
            print(f"Crisp history error: {e}")

        # Get AI reply
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": "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", "anthropic-version": "2023-06-01", "content-type": "application/json"},
                    json={"model": "claude-haiku-4-5-20251001", "max_tokens": 300, "system": CRISP_SYSTEM, "messages": messages_for_ai}
                )
                result = r.json()
                reply = result.get("content", [{}])[0].get("text", "Sorry, I couldn't process that. Please try again.")
        except Exception as e:
            print(f"AI error: {e}")
            reply = "Sorry, I'm having trouble right now. Please try again in a moment."

    # Send reply back to Crisp
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://api.crisp.chat/v1/website/{CRISP_WEBSITE_ID}/conversation/{session_id}/message",
                auth=(CRISP_API_ID, CRISP_API_KEY),
                headers={"X-Crisp-Tier": "plugin", "Content-Type": "application/json"},
                json={"type": "text", "content": reply, "from": "operator", "origin": "chat"}
            )
    except Exception as e:
        print(f"Crisp reply error: {e}")

    return {"ok": True}
