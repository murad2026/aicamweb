with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

with open('escalate_route.py', 'r', encoding='utf-8') as f:
    route = f.read()

if '/chat/escalate' not in content:
    content = content.replace('# Serve frontend', route + '\n# Serve frontend')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Already added')
