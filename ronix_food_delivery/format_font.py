import re

with open('/odoo/odoo16/odoo-custom-addons/ronix_food_delivery/views/food_home_template.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Orange background on 'Tüm Yemekler' pills
content = content.replace(
    'bg-orange-500 px-2 py-1 rounded-pill" style="opacity: 0.9;"',
    'food-bg-orange shadow px-2 py-1 rounded-pill"'
)

# 2. Increase header thickness and slight size
for header in ["Kategoriler", "Favori Restoranlar", "Popüler Yemekler", "Tüm Restoranlar", "Tüm Yemekler"]:
    content = re.sub(
        rf'(<h2 class="food-text-base text-dark mb-[0-3]?)(">)(%s</h2>)' % header,
        r'\1 fw-bolder" style="font-size: 1.125rem !important;"\2\3',
        content
    )

# 3. 'Tümünü Gör' buttons to bold
content = content.replace('fw-medium food-text-orange', 'fw-bolder food-text-orange')

# 4. Prices
content = content.replace('fw-bold food-text-orange', 'fw-bolder food-text-orange')

# 5. Rating numbers, e.g., <span class="fw-medium text-dark">4.5</span>
content = re.sub(
    r'<span class="fw-medium text-dark">([\d\.]+)</span>',
    r'<span class="fw-bold text-dark">\1</span>',
    content
)
content = re.sub(
    r'<span class="food-text-3xs text-secondary fw-medium">([\d\.]+)</span>',
    r'<span class="food-text-xs text-secondary fw-bold">\1</span>',
    content
)
content = re.sub(
    r'<span class="food-text-2xs text-secondary fw-medium">([\d\.]+)</span>',
    r'<span class="food-text-xs text-secondary fw-bold">\1</span>',
    content
)

# 6. Restaurant card titles
content = content.replace('fw-bolder text-dark food-text-sm', 'fw-black text-dark fs-6')

# 7. Food card titles
content = content.replace('fw-bold text-dark food-text-xs', 'fw-bolder text-dark food-text-sm')

# 8. Category names under icons
content = content.replace(
    '<span class="food-text-2xs text-secondary w-100 text-truncate text-center">',
    '<span class="food-text-xs fw-bold text-dark w-100 text-truncate text-center mt-1">'
)

# 9. Offcanvas Image replacement
content = content.replace(
    'src="https://public.readdy.ai/ai/img_res/6f28b0313cb90e72bd38848db907d730.jpg"',
    'src="https://readdy.ai/api/search-image?query=lahmacun%20turkish%20pizza%20with%20minced%20meat%20lemon%20parsley%20restaurant%20photography%20high%20quality&width=600&height=400&seq=lahmacun_hero&orientation=landscape"'
)

# 10. Bottom Navigation Text Thickness
content = content.replace('food-text-2xs mt-1', 'food-text-xs fw-bold mt-1')
content = content.replace('food-text-2xs fw-bold food-text-orange mt-1', 'food-text-xs fw-bolder food-text-orange mt-1')

# 11. Add to cart button text
content = content.replace('fw-semibold food-rounded-xl', 'fw-bold food-rounded-xl')
content = content.replace('fw-semibold text-white', 'fw-bolder text-white')

# 12. Make all `fw-medium` to `fw-semibold` globally for secondary texts
content = content.replace('fw-medium">20-30', 'fw-bold">20-30')
content = content.replace('fw-medium">30-40', 'fw-bold">30-40')


# Revert double classes if any
content = content.replace('fw-bolder fw-bolder', 'fw-bolder')

with open('/odoo/odoo16/odoo-custom-addons/ronix_food_delivery/views/food_home_template.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print("Formatting Complete")

