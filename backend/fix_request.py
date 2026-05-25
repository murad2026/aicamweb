with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = content.replace(
    'from fastapi import FastAPI, Depends, HTTPException',
    'from fastapi import FastAPI, Depends, HTTPException, Request'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
