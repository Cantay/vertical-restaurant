import re

with open('/odoo/odoo16/odoo-custom-addons/ronix_food_delivery/views/food_home_template.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Kategoriler shadow and radius
content = content.replace(
    'class="btn p-0 border-0 bg-transparent w-100 d-flex flex-column align-items-center gap-2"',
    'class="btn p-0 border-0 bg-transparent w-100 d-flex flex-column align-items-center gap-2" style="box-shadow: none !important; border-radius: 0 !important;"'
)

# 2. Tümünü Gör buttons
content = content.replace(
    '<button class="btn btn-link text-decoration-none food-text-xs fw-medium food-text-orange p-0 border-0">Tümünü Gör</button>',
    '<button class="btn btn-link text-decoration-none food-text-xs fw-medium food-text-orange p-0 border-0" style="box-shadow: none !important; border-radius: 0 !important;">Tümünü Gör</button>'
)

# 3. Restoran cards - Favori Restoranlar
content = content.replace(
    '<div class="bg-white  overflow-hidden shadow-sm active-scale cursor-pointer h-100">',
    '<div class="bg-white food-rounded-2xl overflow-hidden shadow active-scale cursor-pointer h-100" onclick="window.location.href=\'/food-restaurant\'">'
)

# 4. Restoran cards - Tüm Restoranlar
content = content.replace(
    '<div class="bg-white  overflow-hidden shadow-sm active-scale cursor-pointer">',
    '<div class="bg-white food-rounded-2xl overflow-hidden shadow active-scale cursor-pointer" onclick="window.location.href=\'/food-restaurant\'">'
)

# 5. Yemek cards - Popüler Yemekler
content = content.replace(
    '<div class="bg-white  overflow-hidden shadow-sm food-min-w-140 active-scale cursor-pointer">',
    '<div class="bg-white food-rounded-2xl overflow-hidden shadow food-min-w-140 active-scale cursor-pointer" data-bs-toggle="offcanvas" data-bs-target="#foodDetailOffcanvas">'
)

# 6. Yemek cards - Tüm Yemekler
content = content.replace(
    '<div class="bg-white  overflow-hidden shadow-sm active-scale cursor-pointer h-100 d-flex flex-column">',
    '<div class="bg-white food-rounded-2xl overflow-hidden shadow active-scale cursor-pointer h-100 d-flex flex-column" data-bs-toggle="offcanvas" data-bs-target="#foodDetailOffcanvas">'
)

with open('/odoo/odoo16/odoo-custom-addons/ronix_food_delivery/views/food_home_template.xml', 'w', encoding='utf-8') as f:
    f.write(content)

with open('/odoo/odoo16/odoo-custom-addons/ronix_food_delivery/views/food_orders_template.xml', 'r', encoding='utf-8') as f:
    orders_content = f.read()

# Fix top padding in orders
orders_content = orders_content.replace(
    '<div class="px-3" style="padding-top: 7rem; padding-bottom: 5rem;">',
    '<div class="px-3" style="padding-top: 9rem; padding-bottom: 5rem;">'
)

with open('/odoo/odoo16/odoo-custom-addons/ronix_food_delivery/views/food_orders_template.xml', 'w', encoding='utf-8') as f:
    f.write(orders_content)

print("Replacement Complete")
