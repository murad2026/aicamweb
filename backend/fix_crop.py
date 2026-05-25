with open('engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''                                    x1,y1,x2,y2 = int(_det["x"]),int(_det["y"]),int(_det["x"])+int(_det["w"]),int(_det["y"])+int(_det["h"])
                                    _crop = frame[y1:y2, x1:x2]'''

new = '''                                    _px = int(_det["w"] * 0.3)
                                    _py = int(_det["h"] * 0.3)
                                    x1 = max(0, int(_det["x"]) - _px)
                                    y1 = max(0, int(_det["y"]) - _py)
                                    x2 = min(frame.shape[1], int(_det["x"]) + int(_det["w"]) + _px)
                                    y2 = min(frame.shape[0], int(_det["y"]) + int(_det["h"]) + _py)
                                    _crop = frame[y1:y2, x1:x2]'''

content = content.replace(old, new)
with open('engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
