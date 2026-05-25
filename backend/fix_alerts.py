with open('engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''                        if self.camera.get("notify_telegram"):
                            chat_id = resolve_chat_id(self.camera["notify_telegram"])
                            if chat_id:
                                tg_chat_id = chat_id
                                tg_msg_id = send_telegram(chat_id, frame, caption)'''

new = '''                        # Get alerts from user settings
                        import sqlite3 as _sq
                        _conn = _sq.connect("C:/aianycam/backend/ai-any-camera.db")
                        _user = _conn.execute("SELECT telegram_chat_id, phone FROM users WHERE id=(SELECT user_id FROM cameras WHERE id=?)", (self.camera["id"],)).fetchone()
                        _conn.close()
                        _tg_from_cam = self.camera.get("notify_telegram")
                        _tg_from_user = _user[0] if _user else None
                        _phone_from_cam = self.camera.get("notify_sms")
                        _phone_from_user = _user[1] if _user else None
                        _tg_target = _tg_from_cam or _tg_from_user
                        _phone_target = _phone_from_cam or _phone_from_user
                        if _tg_target:
                            chat_id = resolve_chat_id(_tg_target)
                            if chat_id:
                                tg_chat_id = chat_id
                                tg_msg_id = send_telegram(chat_id, frame, caption)'''

content = content.replace(old, new)

# Also fix SMS to use _phone_target
old_sms = '''                    if self.camera.get("notify_sms"):
                        try:
                            from photo_service import upload_frame
                            photo_url = upload_frame(frame, self.camera["name"])
                            from sms_service import send_sms
                            msg = caption
                            if photo_url:
                                msg += f" Photo: {photo_url}"
                            send_sms(self.camera["notify_sms"], msg)'''

new_sms = '''                    if _phone_target:
                        try:
                            from sms_service import send_sms
                            msg = caption
                            if photo_url:
                                msg += f" Photo: {photo_url}"
                            send_sms(_phone_target, msg)'''

content = content.replace(old_sms, new_sms)

with open('engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
