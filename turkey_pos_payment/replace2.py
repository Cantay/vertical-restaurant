import os

def replace_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        orig = content
        
        content = content.replace("vpos_order_id", "vvpos_order_id")
        
        if content != orig:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Updated", file_path)
            
    except Exception as e:
        print("Skipped", file_path, e)

for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith(('.py', '.xml', '.csv', '.js')):
            replace_in_file(os.path.join(root, f))
