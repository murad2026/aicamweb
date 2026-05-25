with open('engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''                        photo_url = upload_frame(frame, self.camera["name"])
                        tg_chat_id = None
                        tg_msg_id = None'''

new = '''                        photo_url = upload_frame(frame, self.camera["name"])
                        # Save subject crops for Premium
                        try:
                            from datetime import datetime
                            import sqlite3 as _sq3
                            _c = _sq3.connect("C:/aianycam/backend/ai-any-camera.db")
                            _urow = _c.execute("SELECT plan FROM users WHERE id=(SELECT user_id FROM cameras WHERE id=?)", (self.camera["id"],)).fetchone()
                            _plan = _urow[0] if _urow else "free"
                            _uid = self.camera.get("user_id")
                            if _plan == "premium" and _uid:
                                for _det in in_zone_det:
                                    x1,y1,x2,y2 = int(_det["x1"]),int(_det["y1"]),int(_det["x2"]),int(_det["y2"])
                                    _crop = frame[y1:y2, x1:x2]
                                    if _crop.size > 0:
                                        _crop_url = upload_frame(_crop, f"subject_{self.camera['name']}")
                                        _now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        _c.execute("INSERT INTO subjects (user_id, camera_id, class, photo_url, first_seen, last_seen) VALUES (?,?,?,?,?,?)",
                                                   (_uid, self.camera["id"], _det["class"], _crop_url, _now, _now))
                                _c.commit()
                            _c.close()
                        except Exception as _se:
                            print(f"Subject save error: {_se}")
                        tg_chat_id = None
                        tg_msg_id = None'''

content = content.replace(old, new)
with open('engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
