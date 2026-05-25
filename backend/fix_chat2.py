with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

chat_route = '''
ANTHROPIC_KEY = "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"
AI_SYSTEM = """You are an AI assistant for AI Any Camera - a smart security camera monitoring service. Help users with: finding camera IP (check router at 192.168.1.1), default credentials (Hikvision: admin/12345, Dahua: admin/admin, Axis: root/pass), troubleshooting offline cameras, setting up alerts. Plans: Free 1 camera, Pro /mo 5 cameras, Premium /mo unlimited+subjects. Be helpful and concise."""

@app.post("/chat")
async def chat_endpoint(data: dict):
    import httpx
    messages = data.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="No messages")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 500, "system": AI_SYSTEM, "messages": messages}
        )
        result = r.json()
        text = result.get("content", [{}])[0].get("text", "Sorry, try again.")
        return {"reply": text}
'''

# Remove existing chat route and ANTHROPIC key from end
old_block = '''ANTHROPIC_KEY = "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"
AI_SYSTEM = """You are an AI assistant for AI Any Camera - a smart security camera monitoring service. Help users with: finding camera IP (check router at 192.168.1.1), default credentials (Hikvision: admin/12345, Dahua: admin/admin, Axis: root/pass), troubleshooting offline cameras, setting up alerts. Plans: Free 1 camera, Pro /mo 5 cameras, Premium /mo unlimited+subjects. Be helpful and concise."""
@app.post("/chat")
async def chat_endpoint(data: dict):
    import httpx
    messages = data.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="No messages")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 500, "system": AI_SYSTEM, "messages": messages}
        )
        result = r.json()
        text = result.get("content", [{}])[0].get("text", "Sorry, try again.")
        return {"reply": text}'''

# Insert chat route before StaticFiles mount
old_mount = "# Serve frontend"
new_mount = chat_route + "\n# Serve frontend"

content = content.replace(old_block, '')
content = content.replace(old_mount, new_mount)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
