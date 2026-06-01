content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "            # Decode frame\n            frame_bytes = base64.b64decode(msg[\"frame\"])",
    "            # Decode frame\n            print(f'🖼️ Decoding frame...', flush=True)\n            frame_bytes = base64.b64decode(msg[\"frame\"])"
)
content = content.replace(
    "            if frame is None:\n                continue",
    "            print(f'🖼️ Frame decoded: {frame is not None}', flush=True)\n            if frame is None:\n                continue"
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
