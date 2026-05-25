import cv2
url = 'rtsp://root:Mered123$@192.168.3.105:554/Streaming/Channels/101'
print('Testing:', url)
cap = cv2.VideoCapture(url)
ret, frame = cap.read()
print('Connected:', ret)
cap.release()
