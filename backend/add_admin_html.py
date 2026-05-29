with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

admin_html_route = '''
@app.get("/admin")
def admin_page():
    from fastapi.responses import FileResponse
    import os
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build', 'index.html'))

'''

if '@app.get("/admin")' not in content:
    content = content.replace('# Serve frontend', admin_html_route + '# Serve frontend')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Already exists')
