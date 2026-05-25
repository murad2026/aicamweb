# Добавить в main.py ПЕРЕД строкой "# Serve frontend"

OWNER_PHONE = "+16173724119"  # твой номер для SMS алертов о лидах

@app.post("/chat/escalate")
async def escalate_to_human(data: dict, current_user = Depends(get_current_user)):
    """Send SMS to owner when user requests human agent."""
    from sms_service import send_sms
    username = getattr(current_user, "username", "Unknown")
    email = getattr(current_user, "email", "Unknown")
    plan = getattr(current_user, "plan", "free") or "free"
    last_message = data.get("last_message", "")
    msg = f"AI Any Camera LEAD: {username} ({email}, {plan} plan) wants to talk to a human. Last message: {last_message}"
    try:
        send_sms(OWNER_PHONE, msg)
        return {"ok": True}
    except Exception as e:
        print(f"Escalation SMS error: {e}")
        return {"ok": False}
