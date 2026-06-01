content = open("C:/aianycam/backend/engine.py", encoding="utf-8").read()
content = content.replace(
    '''                        if _tg_target:
                            chat_id = resolve_chat_id(_tg_target)
                            if chat_id:
                                tg_chat_id = chat_id
                                tg_msg_id = send_telegram(chat_id, frame, caption)''',
    '                        # Telegram disabled - handled by agent v5'
)
open("C:/aianycam/backend/engine.py", "w", encoding="utf-8").write(content)
print("Done")
