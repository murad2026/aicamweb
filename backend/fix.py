content = open('main.py', 'r', encoding='utf-8').read()
old = '        if not os.path.exists(tmpfile) or os.path.getsize(tmpfile) == 0:\n            raise HTTPException(status_code=500, detail="Cannot connect to camera")'
new = '        if not os.path.exists(tmpfile) or os.path.getsize(tmpfile) == 0:\n            err = result.stderr.decode() if result.stderr else "no stderr"\n            raise HTTPException(status_code=500, detail=f"Cannot connect: {err}")'
content = content.replace(old, new)
open('main.py', 'w', encoding='utf-8').write(content)
print('Done')
