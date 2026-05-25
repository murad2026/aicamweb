import cv2
url = 'rtsp://root:Mered123%24@192.168.3.171:554/Streaming/Channels/101'
cap = cv2.VideoCapture(url)
ret, frame = cap.read()
print('Connected:', ret)
cap.release()
