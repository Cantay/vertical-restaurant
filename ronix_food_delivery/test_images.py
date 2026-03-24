import odoo
odoo.tools.config.parse_config(['-c', '/etc/odoo16-testodin.conf', '-d', 'testodin'])
registry = odoo.registry('testodin')
with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    restaurant = env['food.restaurant'].search([], limit=1)
    if restaurant:
        print("Image 1920 len:", len(restaurant.image_1920)) if restaurant.image_1920 else print("No image_1920")
        print("Image 512 len:", len(restaurant.image_512)) if restaurant.image_512 else print("No image_512")
    else:
        print("No restaurants found.")
