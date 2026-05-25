import cv2
url = 'rtsp://admin:Mered123$@192.168.3.171:554/Streaming/Channels/101'
cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
ret, frame = cap.read()
print('Connected:', ret)
cap.release()
