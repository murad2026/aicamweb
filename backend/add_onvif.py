from onvif_scanner import probe_onvif, scan_onvif 
class ONVIFRequest(PydanticBase): 
    ip: str 
    port: int = 80 
    username: str = "admin" 
    password: str = "admin" 
f = open('C:/aianycam/backend/main.py', 'a') 
f.write('\n\nfrom onvif_scanner import probe_onvif, scan_onvif\n\nclass ONVIFRequest(PydanticBase):\n    ip: str\n    port: int = 80\n    username: str = "admin"\n    password: str = "admin"\n\n@app.post("/onvif/probe")\ndef onvif_probe(req: ONVIFRequest):\n    result = probe_onvif(req.ip, req.port, req.username, req.password)\n    if not result:\n        raise HTTPException(status_code=404, detail="Camera not found")\n    return result\n\n@app.post("/onvif/scan")\ndef onvif_scan(subnet: str = "192.168.1"):\n    results = scan_onvif(subnet)\n    return {"cameras": results}\n') 
f.close() 
