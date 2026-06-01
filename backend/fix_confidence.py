content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "detections = detect_frame(frame, [\"person\"])",
    "detections = detect_frame(frame, [\"person\"], conf=0.3)"
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
