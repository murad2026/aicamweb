content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "            # Detect\n            from engine import detect_frame, in_zone",
    "            # Detect\n            print(f'🔍 Running detection on frame', flush=True)\n            from engine import detect_frame, in_zone"
)
content = content.replace(
    "            in_zone_det = [d for d in detections if in_zone(d, camera_dict.get(\"zone\"), fw, fh)]",
    "            in_zone_det = [d for d in detections if in_zone(d, camera_dict.get(\"zone\"), fw, fh)]\n            print(f'🔍 Detections: {detections}, in_zone: {in_zone_det}, zone: {camera_dict.get(\"zone\")}', flush=True)"
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
