content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "            # Put frame in detection queue (non-blocking)",
    "            # Save frame for debug\n            import cv2 as _cv2; _cv2.imwrite('C:/aianycam/debug_frame.jpg', frame)\n            # Put frame in detection queue (non-blocking)"
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
