from onvif import ONVIFCamera
import socket
import concurrent.futures

def get_rtsp_url(ip, port=80, username="admin", password="admin"):
    try:
        cam = ONVIFCamera(ip, port, username, password)
        media = cam.create_media_service()
        profiles = media.GetProfiles()
        token = profiles[0].token
        stream_uri = media.GetStreamUri({"StreamSetup": {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}}, "ProfileToken": token})
        return stream_uri.Uri
    except Exception as e:
        return None

def probe_onvif(ip, port=80, username="admin", password="admin"):
    try:
        cam = ONVIFCamera(ip, port, username, password)
        device = cam.create_devicemgmt_service()
        info = device.GetDeviceInformation()
        rtsp = get_rtsp_url(ip, port, username, password)
        return {
            "ip": ip,
            "manufacturer": info.Manufacturer,
            "model": info.Model,
            "rtsp_url": rtsp,
            "username": username,
            "password": password
        }
    except Exception:
        return None

def scan_onvif(subnet="192.168.1", ports=[80, 8080, 8899], credentials=[("admin","admin"),("admin",""),("admin","12345")]):
    results = []
    ips = [f"{subnet}.{i}" for i in range(1, 255)]
    def try_ip(ip):
        for port in ports:
            for user, pwd in credentials:
                result = probe_onvif(ip, port, user, pwd)
                if result:
                    return result
        return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(try_ip, ip): ip for ip in ips}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
    return results
