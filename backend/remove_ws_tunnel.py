with open("C:/aianycam/backend/main.py", encoding="utf-8") as f:
    lines = f.readlines()

# Find start and end of websocket tunnel route
start = None
end = None
for i, line in enumerate(lines):
    if '# ─── WebSocket Tunnel for Remote Cameras' in line:
        start = i
    if start and i > start and line.startswith('@app.post("/api/agent/event")'):
        end = i
        break

print(f"Removing lines {start+1} to {end} ({end-start} lines)")
new_lines = lines[:start] + lines[end:]

with open("C:/aianycam/backend/main.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Done")
