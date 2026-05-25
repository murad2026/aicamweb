with open('engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the event save block and replace it
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'from database import SessionLocal, EventDB' in line:
        indent = '                        '
        new_lines.append(indent + 'from database import SessionLocal, EventDB\n')
        new_lines.append(indent + 'from datetime import datetime\n')
        new_lines.append(indent + 'from photo_service import upload_frame\n')
        new_lines.append(indent + 'photo_url = upload_frame(frame, self.camera["name"])\n')
        new_lines.append(indent + 'tg_chat_id = None\n')
        new_lines.append(indent + 'tg_msg_id = None\n')
        new_lines.append(indent + 'if self.camera.get("notify_telegram"):\n')
        new_lines.append(indent + '    chat_id = resolve_chat_id(self.camera["notify_telegram"])\n')
        new_lines.append(indent + '    if chat_id:\n')
        new_lines.append(indent + '        tg_chat_id = chat_id\n')
        new_lines.append(indent + '        tg_msg_id = send_telegram(chat_id, frame, caption)\n')
        # Skip old lines until db.close()
        while i < len(lines) and 'db.close()' not in lines[i]:
            i += 1
        i += 1  # skip db.close() line
        new_lines.append(indent + 'db = SessionLocal()\n')
        new_lines.append(indent + 'event = EventDB(\n')
        new_lines.append(indent + '    camera_id=self.camera["id"],\n')
        new_lines.append(indent + '    camera_name=self.camera["name"],\n')
        new_lines.append(indent + '    detected=", ".join(set(d["class"] for d in in_zone_det)),\n')
        new_lines.append(indent + '    confidence=f"{max(d[\'conf\'] for d in in_zone_det):.2f}",\n')
        new_lines.append(indent + '    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),\n')
        new_lines.append(indent + '    photo_url=photo_url,\n')
        new_lines.append(indent + '    telegram_chat_id=tg_chat_id,\n')
        new_lines.append(indent + '    telegram_message_id=tg_msg_id\n')
        new_lines.append(indent + ')\n')
        new_lines.append(indent + 'db.add(event)\n')
        new_lines.append(indent + 'db.commit()\n')
        new_lines.append(indent + 'db.close()\n')
        continue
    # Skip old notify_telegram block
    if 'if self.camera.get("notify_telegram")' in line and 'notify_telegram' in line:
        while i < len(lines) and 'send_telegram' not in lines[i]:
            i += 1
        i += 1  # skip send_telegram line
        continue
    new_lines.append(line)
    i += 1

with open('engine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done')
