with open('engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '                                    x1,y1,x2,y2 = int(_det["x1"]),int(_det["y1"]),int(_det["x2"]),int(_det["y2"])'
new = '                                    x1,y1,x2,y2 = int(_det["x"]),int(_det["y"]),int(_det["x"])+int(_det["w"]),int(_det["y"])+int(_det["h"])'

content = content.replace(old, new)
with open('engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
