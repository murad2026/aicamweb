content = open("C:/aianycam/backend/engine.py", encoding="utf-8").read()
content = content.replace(
    '''                        # ── SMS ──────────────────────────────────────────────
                        if _phone_target:
                            try:
                                from sms_service import send_sms
                                msg = caption
                                if photo_url:
                                    msg += f" Photo: {photo_url}"
                                send_sms(_phone_target, msg)
                            except Exception as e:
                                print(f"❌ SMS error: {e}")''',
    '                        # SMS disabled - handled by agent v5'
)
open("C:/aianycam/backend/engine.py", "w", encoding="utf-8").write(content)
print("Done")
