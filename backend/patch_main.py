with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    c = f.read()

with open('main_routes_add.py', 'r', encoding='utf-8') as f:
    routes = f.read()

if '/recognized' not in c:
    c = c.replace('# Serve frontend', routes + '\n# Serve frontend')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('Done')
else:
    print('Already added')
