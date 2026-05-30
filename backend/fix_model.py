content = open("C:/aianycam/backend/main.py", encoding="utf-8").read()
content = content.replace(
    "class RegisterRequest(PydanticBase):\n    email: str\n    username: str\n    password: str",
    "class RegisterRequest(PydanticBase):\n    email: str\n    username: str = ''\n    password: str"
)
open("C:/aianycam/backend/main.py", "w", encoding="utf-8").write(content)
print("Done")
