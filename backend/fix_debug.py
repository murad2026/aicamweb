with open('engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '                        except Exception as _se:\n                            print(f"Subject save error: {_se}")'
new = '                        except Exception as _se:\n                            print(f"Subject save error: {_se}", flush=True)\n                            import traceback; traceback.print_exc()'

content = content.replace(old, new)
with open('engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
