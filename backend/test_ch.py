import cv2
for ch in ['101', '102', '201']:
    url = f'rtsp://root:Mered123$@192.168.3.105:554/Streaming/Channels/{ch}'
    cap = cv2.VideoCapture(url)
    ret, frame = cap.read()
    cap.release()
    print(f'Channel {ch}:', ret)
