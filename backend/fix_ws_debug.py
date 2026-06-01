content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    '    print(f"🔌 Tunnel connected: camera {camera_id} ({cam.name})")',
    '    print(f"🔌 Tunnel connected: camera {camera_id} ({cam.name})", flush=True)'
)
content = content.replace(
    '    except Exception as e:\n        print(f"WS auth error: {e}")\n        import traceback; traceback.print_exc()',
    '    except Exception as e:\n        print(f"WS auth error: {e}", flush=True)\n        import traceback; traceback.print_exc()'
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
