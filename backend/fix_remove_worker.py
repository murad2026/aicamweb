content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()

# Find and remove detection worker block
import re
pattern = r'def _detection_worker\(\):.*?_det_thread\.start\(\)\nprint\("✅ Detection worker started".*?\n'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Also remove queue and thread setup
content = content.replace("import queue as _queue\ndetection_queue = _queue.Queue(maxsize=10)\n", "")
content = content.replace("_last_alert = {}\nimport threading as _threading\n_det_thread = _threading.Thread(target=_detection_worker, daemon=True)\n_det_thread.start()\nprint(\"✅ Detection worker started\", flush=True)", "")

open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
