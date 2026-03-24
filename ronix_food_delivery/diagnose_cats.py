import odoo
odoo.tools.config.parse_config(['-c', '/etc/odoo16-testodin.conf', '-d', 'testodin'])
registry = odoo.registry('testodin')
with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    public_cats = env['product.public.category'].search([])
    for c in public_cats:
        website_id = getattr(c, 'website_id', 'N/A')
        print(f"CAT: {c.name}, Website: {website_id}")
    internal_cats = env['product.category'].search([])
    print(f"INTERNAL_CATEGORIES: {[c.name for c in internal_cats]}")
