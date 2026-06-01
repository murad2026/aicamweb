content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "caption = f\"🚨 {_cam.name}: {', '.join(cls_names)} detected\"",
    "from datetime import datetime\n                _time = datetime.now().strftime('%H:%M:%S')\n                caption = f\"🚨 {_cam.name}: {', '.join(cls_names)} detected at {_time}\""
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
