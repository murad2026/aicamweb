with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '        name, rtsp_url: rtsp, brand: "generic",'
new = '''        const brand = rtsp.includes("axis-media") ? "axis" : rtsp.includes("cam/realmonitor") ? "dahua" : rtsp.includes("Streaming/Channels") ? "hikvision" : "generic";'''

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
