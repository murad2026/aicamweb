with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find admin routes block
admin_start = content.find('ADMIN_PASSWORD = "AiAnyCam2026!"')
serve_start = content.find('# Serve frontend')

if admin_start > serve_start:
    # Admin routes are after StaticFiles - need to move them before
    admin_block = content[admin_start:]
    content_before_serve = content[:serve_start]
    serve_block = content[serve_start:admin_start]
    
    content = content_before_serve + admin_block + '\n' + serve_block
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed - admin routes moved before StaticFiles')
else:
    print('Already in correct order')
