with open('engine.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

old = '_phone_target = self.camera.get("notify_sms") or (_user[1] if _user else None)'
new = '_phone_target = self.camera.get("notify_sms") or None'

if old in content:
    content = content.replace(old, new)
    with open('engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done - SMS will only send if notify_sms is set on camera')
else:
    print('Pattern not found')
    # Show context
    idx = content.find('_phone_target')
    print(repr(content[idx:idx+100]))
