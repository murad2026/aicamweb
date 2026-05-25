with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'async def chat_endpoint(data: dict, current_user = Depends(get_current_user)):'
new = 'async def chat_endpoint(data: dict):'

content = content.replace(old, new)
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
