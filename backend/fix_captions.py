with open('engine.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix caption lines - replace broken emoji patterns
import re

# Fix main caption
content = content.replace(
    "caption = f\"dYs\" {self.camera['name']}: {', '.join(cls_names)} detected\"",
    "caption = f\"🚨 {self.camera['name']}: {', '.join(cls_names)} detected\""
)

# Fix named person caption  
content = content.replace(
    "caption = f\"dY` {_name} detected at {self.camera['name']} (seen {_count}A-)\"",
    "caption = f\"👤 {_name} detected at {self.camera['name']} (seen {_count}x)\""
)

# Fix recurring unknown caption
content = content.replace(
    "caption = f\"dY\", {self.camera['name']}: recurring {_det['class']} detected (seen {_count}A-)\"",
    "caption = f\"🔄 {self.camera['name']}: recurring {_det['class']} detected (seen {_count}x)\""
)

# Fix photo URL double https
content = content.replace(
    'msg += f" Photo: {photo_url}"',
    'msg += f" Photo: {photo_url}"'
)

with open('engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')

# Verify
with open('engine.py', 'r', encoding='utf-8') as f:
    c = f.read()
idx = c.find('caption = f')
print('Caption sample:', repr(c[idx:idx+80]))
