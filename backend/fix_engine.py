content = open('engine.py', 'r', encoding='utf-8').read()
old = '''                    try:
                        from database import SessionLocal, EventDB
                        from datetime import datetime
                        db = SessionLocal()
                        event = EventDB(
                            camera_id=self.camera["id"],
                            camera_name=self.camera["name"],
                            detected=", ".join(set(d["class"] for d in in_zone_det)),
                            confidence=f"{max(d['conf'] for d in in_zone_det):.2f}",
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        db.add(event)
                        db.commit()
                        db.close()
                    except Exception as e:
                        print(f"❌ Event save error: {e}")
                    if self.camera.get("notify_telegram"):
                        chat_id = resolve_chat_id(self.camera["notify_telegram"])
                        if chat_id:
                            send_telegram(chat_id, frame, caption)'''
new = '''                    try:
                        from database import SessionLocal, EventDB
                        from datetime import datetime
                        from photo_service import upload_frame
                        photo_url = upload_frame(frame, self.camera["name"])
                        db = SessionLocal()
                        tg_chat_id = None
                        tg_msg_id = None
                        if self.camera.get("notify_telegram"):
                            chat_id = resolve_chat_id(self.camera["notify_telegram"])
                            if chat_id:
                                tg_chat_id = chat_id
                                tg_msg_id = send_telegram(chat_id, frame, caption)
                        event = EventDB(
                            camera_id=self.camera["id"],
                            camera_name=self.camera["name"],
                            detected=", ".join(set(d["class"] for d in in_zone_det)),
                            confidence=f"{max(d['conf'] for d in in_zone_det):.2f}",
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            photo_url=photo_url,
                            telegram_chat_id=tg_chat_id,
                            telegram_message_id=tg_msg_id
                        )
                        db.add(event)
                        db.commit()
                        db.close()
                    except Exception as e:
                        print(f"❌ Event save error: {e}")'''
content = content.replace(old, new)
open('engine.py', 'w', encoding='utf-8').write(content)
print('Done' if old in open('engine.py', 'r', encoding='utf-8').read() == False else 'Replaced')
