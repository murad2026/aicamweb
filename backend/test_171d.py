import cv2
import os
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
url = 'rtsp://root:Mered123$@192.168.3.171:554/Streaming/Channels/101'
cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
ret, frame = cap.read()
print('Connected:', ret)
cap.release()
