with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

with open('crisp_webhook.py', 'r', encoding='utf-8') as f:
    route = f.read()

# Add Request to fastapi imports
if 'from fastapi import' in content and 'Request' not in content:
    content = content.replace('from fastapi import FastAPI,', 'from fastapi import FastAPI, Request,')

if '/crisp/webhook' not in content:
    content = content.replace('# Serve frontend', route + '\n# Serve frontend')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Already added')
