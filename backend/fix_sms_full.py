content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    '''            # Ensure SMS fits in 160 chars
            if len(msg) > 160:
                msg = msg[:157] + "..."''',
    ''
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
