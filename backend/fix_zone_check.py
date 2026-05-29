with open('engine.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

old = '''def in_zone(p, zone, frame_w, frame_h, grid_cols=16, grid_rows=9):
    if not zone or not zone.get("cells"):
        return True'''

new = '''def in_zone(p, zone, frame_w, frame_h, grid_cols=16, grid_rows=9):
    if not zone or not zone.get("cells"):
        return False  # No zone = no alerts'''

if old in content:
    content = content.replace(old, new)
    with open('engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done - no alerts without zone')
else:
    print('Pattern not found')
    idx = content.find('def in_zone')
    print(repr(content[idx:idx+150]))
