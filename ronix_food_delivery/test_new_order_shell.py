env['sale.order'].create({'partner_id': 1, 'is_food_order': True, 'state': 'sale', 'food_restaurant_id': 1})
env.cr.commit()
print('Order created successfully')
