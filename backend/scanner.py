import socket
import threading
import cv2

def check_port(ip, port, timeout=0.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def get_local_subnet():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}"
    except:
        return "192.168.1"

def scan_network():
    subnet = get_local_subnet()
    found = []
    lock = threading.Lock()
    def check_ip(i):
        ip = f"{subnet}.{i}"
        if check_port(ip, 554):
            with lock:
                found.append({"ip": ip, "port": 554, "type": "rtsp"})
        elif check_port(ip, 7441):
            with lock:
                found.append({"ip": ip, "port": 7441, "type": "unifi"})
    threads = []
    for i in range(1, 255):
        t = threading.Thread(target=check_ip, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join(timeout=2)
    return found

def test_rtsp(ip, username, password, brand="auto"):
    paths = {
        "hikvision": f"rtsp://{username}:{password}@{ip}:554/Streaming/Channels/101",
        "dahua": f"rtsp://{username}:{password}@{ip}:554/cam/realmonitor?channel=1&subtype=0",
        "reolink": f"rtsp://{username}:{password}@{ip}:554/h264Preview_01_main",
        "generic": f"rtsp://{username}:{password}@{ip}:554/stream1",
    }
    if brand != "auto" and brand in paths:
        to_try = {brand: paths[brand]}
    else:
        to_try = paths
    for brand_name, url in to_try.items():
        try:
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            ret, _ = cap.read()
            cap.release()
            if ret:
                return {"success": True, "rtsp_url": url, "brand": brand_name}
        except:
            continue
    return {"success": False}
