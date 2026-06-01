with open("C:/aianycam/backend/main.py", encoding="utf-8") as f:
    lines = f.readlines()

start = None
end = None
for i, line in enumerate(lines):
    if '# ─── WebSocket Tunnel for Remote Cameras' in line or 'WebSocket Tunnel for Remote Cameras' in line:
        start = i
    if start and i > start and ('# Serve frontend' in line or '@app.post("/api/agent/event")' in line):
        end = i
        break

if start and end:
    print(f"Removing lines {start+1} to {end}")
    new_lines = lines[:start] + lines[end:]
    with open("C:/aianycam/backend/main.py", "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Done")
else:
    print(f"Not found: start={start}, end={end}")
