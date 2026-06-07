content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "                if photo_url:\n                    msg += f\" {photo_url}\"",
    "                if photo_url:\n                    import time as _t\n                    cache_bust = f\"{photo_url}?v={int(_t.time())}\"\n                    msg += f\" {cache_bust}\""
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
