import cv2

dvrs = [
    ("192.168.3.88", "DVR 1"),
    ("192.168.3.90", "DVR 2"),
    ("192.168.3.98", "DVR 3"),
]

for ip, name in dvrs:
    print(f"\n=== {name} ({ip}) ===")
    for ch in range(1, 5):  # test first 4 channels
        url = f"rtsp://admin:Mered123$@{ip}:554/cam/realmonitor?channel={ch}&subtype=0"
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 8000)
        ret, _ = cap.read()
        cap.release()
        status = "OK" if ret else "FAIL"
        print(f"  Channel {ch}: {status}")
