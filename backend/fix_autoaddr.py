with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix the broken line
content = content.replace(
    'detect_classes: List[str] = ["person"]\n    name: Optional[str] = None',
    'detect_classes: List[str] = ["person"]\n    name: Optional[str] = None'
)

# Also fix literal \n if present
content = content.replace(
    'detect_classes: List[str] = ["person"]\\n    name: Optional[str] = None',
    'detect_classes: List[str] = ["person"]\n    name: Optional[str] = None'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
