content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    '''            msg = caption
            if photo_url:
                import re, time
                match = re.search(r\'/v(\\d+)/\', photo_url)
                if match:
                    photo_ts = int(match.group(1))
                    age = int(time.time()) - photo_ts
                    if age > 60:
                        print(f"Photo too old ({age}s), skipping URL")
                        photo_url = None
                if photo_url:
                    import time as _t
                    cache_bust = f"{photo_url}?v={int(_t.time())}"
                    msg += f" {cache_bust}"''',
    '''            msg = caption
            if photo_url:
                import re, time as _t
                match = re.search(r\'/v(\\d+)/\', photo_url)
                if match:
                    photo_ts = int(match.group(1))
                    age = int(_t.time()) - photo_ts
                    if age > 120:
                        print(f"Photo too old ({age}s), skipping URL")
                        photo_url = None
                if photo_url:
                    msg += f" aianycamera.com/events"'''
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
