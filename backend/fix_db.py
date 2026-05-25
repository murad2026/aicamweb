with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '    phone = Column(String, nullable=True)'
new = '    phone = Column(String, nullable=True)\n    phone_verified = Column(Integer, default=0)\n    plan = Column(String, default="free")'

content = content.replace(old, new)
with open('database.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
