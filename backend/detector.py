import cv2
import numpy as np

model = None

CLASS_NAMES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    15: "cat",
    16: "dog"
}

def get_model():
    global model
    if model is None:
        from ultralytics import YOLO
        model = YOLO("/Users/mg2-152/ai-any-camera/backend/yolov8s.pt")
    return model

def detect_frame(frame, conf_threshold=0.5):
    m = get_model()
    results = m(frame, verbose=False)[0]
    detections = []
    for box in results.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        if cls in CLASS_NAMES and conf >= conf_threshold:
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            detections.append({
                "class": CLASS_NAMES[cls],
                "conf": round(conf, 2),
                "x": x1, "y": y1,
                "w": x2-x1, "h": y2-y1
            })
    return detections

def detect_image_bytes(image_bytes, conf_threshold=0.5):
    arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return detect_frame(frame, conf_threshold)
