import os

def replace_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        orig = content
        
        # order line
        content = content.replace("'vpos.order.line'", "'vpos.order.line'")
        content = content.replace('"vpos.order.line"', '"vpos.order.line"')
        content = content.replace(">vpos.order.line<", ">vpos.order.line<")
        content = content.replace("model_vpos_order_line", "model_vpos_order_line")
        content = content.replace("vpos.order.line,", "vvpos.order.line,")
        
        # order
        content = content.replace("'vpos.order'", "'vpos.order'")
        content = content.replace('"vpos.order"', '"vpos.order"')
        content = content.replace(">vpos.order<", ">vpos.order<")
        content = content.replace("model_vpos_order", "model_vpos_order")
        content = content.replace("vpos.order,", "vvpos.order,")
        
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
