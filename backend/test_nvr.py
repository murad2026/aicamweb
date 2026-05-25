import cv2

url = "rtsp://admin:Mered123$@192.168.3.102:554/cam/realmonitor?channel=1&subtype=0"
print(f"Testing: {url}")
cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 8000)
ret, _ = cap.read()
cap.release()
print("OK - Channel 1 works!" if ret else "FAIL - Cannot connect")

# Test channel 2
url2 = "rtsp://admin:Mered123$@192.168.3.102:554/cam/realmonitor?channel=2&subtype=0"
cap2 = cv2.VideoCapture(url2, cv2.CAP_FFMPEG)
cap2.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 8000)
ret2, _ = cap2.read()
cap2.release()
print("OK - Channel 2 works!" if ret2 else "FAIL - Channel 2 not found")
