content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "    return {`message`: `Check your email to verify your account`}",
    '    return {"message": "Check your email to verify your account"}'
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
