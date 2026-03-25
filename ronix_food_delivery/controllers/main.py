# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class FoodDeliveryController(http.Controller):
    def _serialize_review(self, review, rating_field='rating'):
        partner_name = review.partner_id.name or 'Kullanici'
        masked_name = partner_name[:2] + '***' if len(partner_name) > 2 else partner_name
        return {
            'id': review.id,
            'author': masked_name,
            'date': review.create_date.strftime('%d %b %Y') if review.create_date else '',
            'rating': int(getattr(review, rating_field, 0) or 0),
            'comment': review.comment or '',
            'tags': review.tag_ids.mapped('name'),
        }

    @http.route('/food-home', type='http', auth="public", website=True)
    def food_home(self, **kwargs):
        partner = request.env.user.partner_id
        company = request.env.company
        
        popular_restaurants = request.env['food.restaurant'].sudo().search([('active', '=', True), ('is_open', '=', True), ('is_grocery', '=', False)], limit=12)
        grocery_stores = request.env['food.restaurant'].sudo().search([('active', '=', True), ('is_open', '=', True), ('is_grocery', '=', True)], limit=12)
        
        all_favorites = request.env['food.restaurant'].sudo().search([('favorite_user_ids', 'in', request.env.user.id), ('active', '=', True), ('is_open', '=', True)])
        favorite_restaurants = all_favorites.filtered(lambda r: not r.is_grocery)[:8]
        favorite_groceries = all_favorites.filtered(lambda r: r.is_grocery)[:8]
        
        # Load categories
        categories = request.env['product.public.category'].sudo().search([], limit=12)
        
        # Load foods - Exclude grocery products from global feed
        popular_foods = request.env['product.template'].sudo().search([('food_restaurant_id.is_open', '=', True), ('food_restaurant_id.is_grocery', '=', False), ('is_food', '=', True), ('is_published', '=', True)], order='food_rating desc', limit=10)
        all_foods = request.env['product.template'].sudo().search([('food_restaurant_id.is_open', '=', True), ('food_restaurant_id.is_grocery', '=', False), ('is_food', '=', True), ('is_published', '=', True)], limit=20)
        
        values = {
            'partner': partner,
            'current_address': partner.current_food_address_id,
            'addresses': partner.food_address_ids,
            'google_maps_api_key': company.x_google_maps_geocode_api_key if hasattr(company, 'x_google_maps_geocode_api_key') else False,
            'popular_restaurants': popular_restaurants,
            'grocery_stores': grocery_stores,
            'favorite_restaurants': favorite_restaurants,
            'favorite_groceries': favorite_groceries,
            'categories': categories,
            'popular_foods': popular_foods,
            'all_foods': all_foods,
            'order': self._get_cart_order(),
        }
        return request.render('ronix_food_delivery.food_home_page', values)

    @http.route('/food-cart', type='http', auth="user", website=True)
    def food_cart(self, **kwargs):
        order = self._get_cart_order()
        values = {
            'order': order,
        }
        return request.render('ronix_food_delivery.food_cart_page', values)

    @http.route('/food-orders', type='http', auth="user", website=True)
    def food_orders(self, **kwargs):
        partner = request.env.user.partner_id
        all_orders = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('is_food_order', '=', True),
            ('is_tip_order', '=', False),
            ('state', 'in', ('sale', 'cancel')),  # Exclude draft/cart orders
        ], order='date_order desc')

        # Active = confirmed (paid) orders that are still in progress (not yet delivered)
        active_orders = all_orders.filtered(
            lambda o: o.state == 'sale' and o.food_delivery_status in ('preparing', 'on_the_way')
        )
        # Past = delivered, cancelled, or done orders
        past_orders = all_orders.filtered(
            lambda o: o.state == 'cancel' or
                      (o.state == 'sale' and o.food_delivery_status in ('delivered', 'cancelled'))
        )

        return request.render('ronix_food_delivery.food_orders_page', {
            'active_orders': active_orders,
            'past_orders': past_orders,
            'active_count': len(active_orders),
        })

    @http.route('/ronix_food_delivery/check_new_orders', type='json', auth="user")
    def check_new_orders(self, last_check_time=None, **kwargs):
        # Must be in proper security group.
        if not request.env.user.has_group('ronix_food_delivery.group_food_shop_manager'):
            return {'orders': []}
            
        domain = [
            ('is_food_order', '=', True),
            ('is_tip_order', '=', False),
            ('food_alert_acknowledged', '=', False), # Only unacknowledged alerts
            ('state', 'not in', ('draft', 'sent', 'cancel')), # Only confirmed/paid orders
        ]
        if last_check_time:
            domain.append(('date_order', '>', last_check_time))
            
        # Refine domain for non-admins to ensure they ONLY see their own restaurant's orders
        if not request.env.user.has_group('ronix_food_delivery.group_food_admin'):
            # Find restaurants where this user is a manager
            allowed_restaurants = request.env['food.restaurant'].sudo().search([
                ('manager_ids', 'in', request.env.user.id)
            ])
            domain.append(('food_restaurant_id', 'in', allowed_restaurants.ids))
            
        # Search WITH .sudo() but with manual restaurant filtering (more robust than IR rules alone in RPC)
        new_orders = request.env['sale.order'].sudo().search(domain, order='date_order asc')
        
        result = []
        for o in new_orders:
            lines = []
            for line in o.order_line:
                addons = []
                if hasattr(line, 'food_line_addon_ids'):
                    for addon in line.food_line_addon_ids:
                        addons.append({
                            'name': addon.addon_id.name,
                            'qty': int(addon.quantity),
                        })
                        
                lines.append({
                    'name': line.product_id.name,
                    'qty': int(line.product_uom_qty),
                    'price_total': line.price_total,
                    'addons': addons,
                })
                
            result.append({
                'id': o.id,
                'name': o.name,
                'customer_name': o.food_customer_name or o.partner_id.name,
                'customer_phone': o.partner_id.mobile or o.partner_id.phone or '',
                'restaurant_name': o.food_restaurant_id.name if o.food_restaurant_id else 'Bilinmeyen Restoran',
                'amount_total': o.amount_total,
                'date_order': str(o.date_order),
                'address': o.food_delivery_address_text or '',
                'notes': o.food_order_notes or '',
                'lines': lines,
            })
            
        return {'orders': result}

    @http.route('/ronix_food_delivery/acknowledge_order_alert', type='json', auth="user")
    def acknowledge_order_alert(self, order_id, **kwargs):
        if not request.env.user.has_group('ronix_food_delivery.group_food_shop_manager'):
            return {'success': False, 'error': 'Access Denied'}
            
        # Browse WITHOUT .sudo() first to check access
        order = request.env['sale.order'].browse(order_id)
        if order.exists() and order.is_food_order:
            # We use sudo for write to ensure it goes through even if they have read-only access but are managers
            order.sudo().write({'food_alert_acknowledged': True})
            return {'success': True}
            
        return {'success': False, 'error': 'Order not found'}

    @http.route('/food-profile', type='http', auth="user", website=True)
    def food_profile(self, **kwargs):
        partner = request.env.user.partner_id
        company = request.env.company
        values = {
            'partner': partner,
            'addresses': partner.food_address_ids,
            'google_maps_api_key': company.x_google_maps_geocode_api_key if hasattr(company, 'x_google_maps_geocode_api_key') else False,
        }
        return request.render('ronix_food_delivery.food_profile_page', values)

    @http.route(['/food-restaurant', '/food-restaurant/<model("food.restaurant"):restaurant>'], type='http', auth="public", website=True)
    def food_restaurant(self, restaurant=None, **kwargs):
        if not restaurant or not restaurant.is_open or not restaurant.active:
            return request.redirect('/food-home')
            
        restaurant_foods = request.env['product.template'].sudo().search([('food_restaurant_id', '=', restaurant.id), ('is_food', '=', True), ('is_published', '=', True)])
        
        values = {
            'restaurant': restaurant,
            'restaurant_foods': restaurant_foods,
            'order': self._get_cart_order(),
        }
        return request.render('ronix_food_delivery.food_restaurant_page', values)

    @http.route('/food-favorites', type='http', auth="user", website=True)
    def food_favorites(self, q=None, order_by=None, is_grocery=None, **kwargs):
        domain = [('favorite_user_ids', 'in', request.env.user.id), ('active', '=', True), ('is_open', '=', True)]
        if is_grocery is not None:
            domain.append(('is_grocery', '=', is_grocery == 'True' or is_grocery is True))
        if q:
            domain.append(('name', 'ilike', q))
            
        order = 'name asc'
        if order_by == 'rating':
            order = 'rating desc'
        elif order_by == 'delivery':
            order = 'delivery_time_min asc'
            
        favorite_restaurants = request.env['food.restaurant'].sudo().search(domain, order=order)
        values = {
            'favorite_restaurants': favorite_restaurants,
            'q': q,
            'active_order_by': order_by,
            'order': self._get_cart_order(),
        }
        return request.render('ronix_food_delivery.food_favorite_restaurants_page', values)

    @http.route('/food/toggle_favorite', type='json', auth="user", website=True)
    def toggle_favorite(self, restaurant_id, **kwargs):
        restaurant = request.env['food.restaurant'].sudo().browse(int(restaurant_id))
        if not restaurant.exists():
            return {'error': 'Restaurant not found'}
        
        user_id = request.env.user.id
        if request.env.user in restaurant.favorite_user_ids:
            restaurant.sudo().favorite_user_ids = [(3, user_id)]
            is_favorite = False
        else:
            restaurant.sudo().favorite_user_ids = [(4, user_id)]
            is_favorite = True
            
        return {'is_favorite': is_favorite}

    @http.route('/food/toggle_favorite_food', type='json', auth="user", website=True)
    def toggle_favorite_food(self, food_id, **kwargs):
        food = request.env['product.template'].sudo().browse(int(food_id))
        if not food.exists() or not food.is_food:
            return {'error': 'Food not found'}
        
        user_id = request.env.user.id
        if request.env.user in food.food_favorite_user_ids:
            food.sudo().food_favorite_user_ids = [(3, user_id)]
            is_favorite = False
        else:
            food.sudo().food_favorite_user_ids = [(4, user_id)]
            is_favorite = True
            
        return {'is_favorite': is_favorite}

    @http.route('/food-account', type='http', auth="user", website=True)
    def food_account(self, **kwargs):
        return request.render('ronix_food_delivery.food_account_page', {})

    @http.route('/food-account/update', type='http', auth="user", website=True, methods=['POST'])
    def food_account_update(self, **post):
        partner = request.env.user.partner_id
        update_vals = {}
        if post.get('name'):
            update_vals['name'] = post.get('name')
        if post.get('email'):
            update_vals['email'] = post.get('email')
        if 'mobile' in post:
            update_vals['mobile'] = post.get('mobile')

        if update_vals:
            partner.sudo().write(update_vals)

        return request.redirect('/food-account?success=1')

    @http.route('/food-addresses', type='http', auth="user", website=True)
    def food_addresses(self, **kwargs):
        partner = request.env.user.partner_id
        company = request.env.company
        values = {
            'addresses': partner.food_address_ids,
            'google_maps_api_key': company.x_google_maps_geocode_api_key if hasattr(company, 'x_google_maps_geocode_api_key') else False,
        }
        return request.render('ronix_food_delivery.food_addresses_page', values)

    @http.route('/food-payment-methods', type='http', auth="user", website=True)
    def food_payment_methods(self, **kwargs):
        partner_sudo = request.env.user.partner_id
        tokens = request.env['payment.token'].sudo()._get_available_tokens(
            None, partner_sudo.id
        )
        return request.render('ronix_food_delivery.food_payment_methods_page', {
            'tokens': tokens
        })

    @http.route('/food/checkout/payment', type='http', auth="user", website=True)
    def food_checkout_payment(self, **kwargs):
        order = self._get_cart_order()
        if not order or not order.order_line:
            return request.redirect('/food-cart')
            
        # Check min order amount
        if order.amount_untaxed < (order.food_restaurant_id.min_order_amount or 0.0):
            return request.redirect('/food-cart?error=min_amount')
            
        partner_sudo = request.env.user.partner_id
        tokens = request.env['payment.token'].sudo()._get_available_tokens(
            None, partner_sudo.id
        )
        
        # Ensure at least one default
        if not tokens.filtered(lambda t: t.default_card) and tokens:
            tokens[0].sudo().write({'default_card': True})

        return request.render('ronix_food_delivery.food_checkout_payment_template', {
            'order': order,
            'tokens': tokens,
        })

    @http.route('/food/checkout/confirm', type='json', auth="user", website=True)
    def food_checkout_confirm(self, token_id=None, **kwargs):
        order = self._get_cart_order()
        if not order or not order.order_line:
            return {'error': 'Sepetiniz boş.'}
            
        # Check min order amount
        if order.amount_untaxed < (order.food_restaurant_id.min_order_amount or 0.0):
            return {'error': f"Sipariş tutarı minimum {order.food_restaurant_id.min_order_amount} TL olmalıdır."}
            
        if not token_id:
            return {'error': 'Lütfen bir ödeme yöntemi seçin.'}
            
        # Link current address to order
        address = request.env.user.partner_id.current_food_address_id
        if address:
            addr_text = f"{address.address_details or ''}"
            if address.address_directions:
                addr_text += f" ({address.address_directions})"
            order.sudo().write({
                'food_delivery_address_id': address.id,
                'food_delivery_address_text': addr_text,
                'food_customer_name': request.env.user.partner_id.name
            })
            
        token = request.env['payment.token'].sudo().search([
            ('id', '=', int(token_id)),
            ('partner_id', '=', request.env.user.partner_id.id)
        ])
        
        if not token:
            return {'error': 'Geçersiz ödeme yöntemi.'}
            
        # Set as default
        all_tokens = request.env['payment.token'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ])
        all_tokens.sudo().write({'default_card': False})
        token.sudo().write({'default_card': True})
        
        # Charge
        user_login = request.env.user.login
        if user_login == '+905559999999':
            # Bypass payment for test user
            order.sudo().write({'payment_status': 'paid'})
            order.sudo().action_confirm()
            result = True
        else:
            result = order.action_stripe_charge_saved_card()
        
        if order.payment_status == 'paid':
            return {
                'success': True,
                'order_id': order.id,
                'message': 'Siparişiniz başarıyla alındı!'
            }
        else:
            error_msg = 'Ödeme işlemi başarısız oldu.'
            if isinstance(result, dict) and result.get('last_payment_error'):
                error_msg = result['last_payment_error'].get('message', error_msg)
            return {'error': error_msg}

    @http.route('/food-settings', type='http', auth="user", website=True)
    def food_settings(self, **kwargs):
        return request.render('ronix_food_delivery.food_settings_page', {})

    @http.route('/food-support', type='http', auth="user", website=True)
    def food_support(self, **kwargs):
        return request.render('ronix_food_delivery.food_support_page', {})

    @http.route('/food-coupons', type='http', auth="user", website=True)
    def food_coupons(self, **kwargs):
        return request.render('ronix_food_delivery.food_coupons_page', {})

    @http.route('/food-notifications', type='http', auth="user", website=True)
    def food_notifications(self, **kwargs):
        return request.render('ronix_food_delivery.food_notifications_page', {})

    @http.route('/food-all-restaurants', type='http', auth="public", website=True)
    def food_all_restaurants(self, q=None, order_by=None, is_grocery=False, **kwargs):
        domain = [('active', '=', True), ('is_open', '=', True), ('is_grocery', '=', is_grocery)]
        if q:
            domain.append(('name', 'ilike', q))
            
        order = 'name asc'
        if order_by == 'rating':
            order = 'rating desc'
        elif order_by == 'delivery':
            order = 'delivery_time_min asc'
            
        restaurants = request.env['food.restaurant'].sudo().search(domain, order=order)
        values = {
            'restaurants': restaurants,
            'q': q,
            'active_order_by': order_by,
            'order': self._get_cart_order(),
        }
        return request.render('ronix_food_delivery.food_all_restaurants_page', values)

    @http.route('/food-popular-foods', type='http', auth="public", website=True)
    def food_popular_foods(self, category_id=None, order_by=None, q=None, **kwargs):
        domain = [('food_restaurant_id.is_open', '=', True), ('food_restaurant_id.is_grocery', '=', False), ('is_food', '=', True), ('is_published', '=', True)]
        if category_id:
            domain.append(('public_categ_ids', 'in', int(category_id)))
        if q:
            domain.append(('name', 'ilike', q))
            
        # Define sorting
        order = 'food_rating desc' # Default
        if order_by == 'rating':
            order = 'food_rating desc'
        elif order_by == 'price':
            order = 'list_price asc'
        elif order_by == 'delivery':
            order = 'food_restaurant_id asc, food_rating desc'
            
        popular_foods = request.env['product.template'].sudo().search(domain, order=order, limit=40)
        
        # If order_by is delivery, we should ideally sort by delivery_time_min
        if order_by == 'delivery':
            popular_foods = popular_foods.sorted(key=lambda f: f.food_restaurant_id.delivery_time_min)

        categories = request.env['product.public.category'].sudo().search([], limit=12)
        
        values = {
            'popular_foods': popular_foods,
            'categories': categories,
            'active_category_id': int(category_id) if category_id else None,
            'active_order_by': order_by,
            'q': q,
            'order': self._get_cart_order(),
        }
        return request.render('ronix_food_delivery.food_popular_foods_page', values)

    @http.route('/food/offcanvas/<int:food_id>', type='json', auth="public", website=True)
    def get_food_offcanvas_content(self, food_id, **kwargs):
        food = request.env['product.template'].sudo().browse(food_id)
        if not food.exists():
            return '<div class="p-4 text-center text-danger">Yemek bulunamadı.</div>'

        values = {'food': food}
        # Pass combo data for combo products
        if food.type == 'combo' and food.combo_ids:
            values['is_combo'] = True
            values['combo_choices'] = food.combo_ids

        return request.env['ir.ui.view']._render_template('ronix_food_delivery.food_detail_offcanvas_content', values)

    @http.route('/food/reviews', type='json', auth="public", website=True)
    def food_reviews(self, review_type, record_id, offset=0, limit=20, rating=None, **kwargs):
        offset = int(offset or 0)
        limit = min(int(limit or 20), 50)
        rating = int(rating) if rating not in (False, None, '', 'all') else False

        if review_type == 'restaurant':
            record = request.env['food.restaurant'].sudo().browse(int(record_id))
            if not record.exists():
                return {'reviews': [], 'has_more': False, 'total': 0}
            domain = [('restaurant_id', '=', record.id)]
            model = request.env['food.restaurant.review'].sudo()
            rating_field = 'rating'
        elif review_type == 'food':
            record = request.env['product.template'].sudo().browse(int(record_id))
            if not record.exists() or not record.is_food:
                return {'reviews': [], 'has_more': False, 'total': 0}
            domain = [('product_id', '=', record.id)]
            model = request.env['food.product.review'].sudo()
            rating_field = 'rating'
        else:
            return {'reviews': [], 'has_more': False, 'total': 0}

        if rating:
            domain.append((rating_field, '=', rating))

        total = model.search_count(domain)
        reviews = model.search(domain, order='create_date desc', offset=offset, limit=limit)
        return {
            'reviews': [self._serialize_review(review, rating_field=rating_field) for review in reviews],
            'has_more': offset + len(reviews) < total,
            'total': total,
        }

    # Cart Management
    def _get_cart_order(self, create=False):
        if request.env.user._is_public():
            return request.env['sale.order']
            
        partner = request.env.user.partner_id
        order = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'draft'),
            ('is_food_order', '=', True)
        ], order='id desc', limit=1)
        
        if not order and create:
            order = request.env['sale.order'].sudo().create({
                'partner_id': partner.id,
                'is_food_order': True,
            })
            
        # Ensure address is synced and fee is calculated
        if order and partner.current_food_address_id:
            if not order.food_delivery_address_id or order.food_delivery_address_id.id != partner.current_food_address_id.id:
                order.sudo().write({
                    'food_delivery_address_id': partner.current_food_address_id.id,
                    'food_delivery_address_text': partner.current_food_address_id.address_details,
                })
                order.sudo().action_calculate_delivery_fee()
            elif order.food_delivery_fee == 0.0:
                # Proactively calculate if fee is 0 and we have an address
                order.sudo().action_calculate_delivery_fee()
            
        return order

    @http.route('/food/cart/add_json', type='json', auth="user", website=True)
    def food_cart_add_json(self, product_id, quantity=1, addons=None, combo_items=None, **kwargs):
        partner = request.env.user.partner_id
        if not partner.current_food_address_id:
            return {'error': 'address_required'}

        order = self._get_cart_order(create=True)
        product = request.env['product.template'].sudo().browse(int(product_id))

        if not product.exists():
            return {'error': 'Yemek bulunamadı.'}

        if not order.food_restaurant_id:
            order.sudo().write({'food_restaurant_id': product.food_restaurant_id.id})
        elif order.food_restaurant_id.id != product.food_restaurant_id.id:
            return {
                'error': 'different_restaurant',
                'current_restaurant': order.food_restaurant_id.name,
                'new_restaurant': product.food_restaurant_id.name
            }

        product_product = request.env['product.product'].sudo().search([('product_tmpl_id', '=', product.id)], limit=1)

        # Combo product flow
        if product.type == 'combo' and combo_items:
            self._add_combo_to_cart(order, product_product, quantity, combo_items)
        else:
            # Regular product flow
            # Process addons: list of {'id': addon_id, 'qty': qty}
            addons_data = addons or []
            addons_data = sorted(addons_data, key=lambda x: int(x['id']))
            for a in addons_data:
                a['id'] = int(a['id'])
                a['qty'] = int(a.get('qty', 1))

            # Enhanced comparison for identical lines
            existing_line = False
            for line in order.order_line.filtered(lambda l: l.product_id.id == product_product.id and not l.combo_item_id):
                line_addons = sorted([{ 'id': a.addon_id.id, 'qty': a.quantity } for a in line.food_line_addon_ids], key=lambda x: x['id'])
                if line_addons == addons_data:
                    existing_line = line
                    break

            if existing_line:
                existing_line.sudo().write({
                    'product_uom_qty': existing_line.product_uom_qty + quantity
                })
            else:
                line_vals = {
                    'order_id': order.id,
                    'product_id': product_product.id,
                    'product_uom_qty': quantity,
                }
                new_line = request.env['sale.order.line'].sudo().create(line_vals)

                # Create addon lines
                for addon_item in addons_data:
                    request.env['sale.order.line.food.addon'].sudo().create({
                        'line_id': new_line.id,
                        'addon_id': addon_item['id'],
                        'quantity': addon_item['qty'],
                    })
                # Trigger price recompute
                new_line.sudo()._compute_price_unit()

        # Ensure delivery fee line is present and total is updated
        order.sudo().action_calculate_delivery_fee()
        order.sudo().invalidate_recordset(['amount_untaxed', 'amount_tax', 'amount_total'])

        return self._get_cart_summary_data(order)

    def _add_combo_to_cart(self, order, combo_product, quantity, combo_items):
        """Create combo parent line + child lines with linked_line_id and combo_item_id."""
        SOL = request.env['sale.order.line'].sudo()

        # Create parent combo line (price will be 0 by Odoo design)
        combo_line = SOL.create({
            'order_id': order.id,
            'product_id': combo_product.id,
            'product_uom_qty': quantity,
        })

        # Create child lines for each selected combo item
        for item_data in combo_items:
            combo_item = request.env['product.combo.item'].sudo().browse(int(item_data['combo_item_id']))
            if not combo_item.exists():
                continue
            SOL.create({
                'order_id': order.id,
                'product_id': combo_item.product_id.id,
                'product_uom_qty': quantity,
                'linked_line_id': combo_line.id,
                'combo_item_id': combo_item.id,
            })

    def _get_cart_summary_data(self, order):
        """Return cart summary dict, excluding combo child lines from quantity count."""
        food_lines = order.order_line.filtered(
            lambda l: l.product_id.is_food and not l.combo_item_id
        )
        return {
            'cart_quantity': sum(food_lines.mapped('product_uom_qty')),
            'cart_untaxed': order.amount_untaxed - order.food_delivery_fee,
            'cart_tax': order.amount_tax,
            'cart_delivery_fee': order.food_delivery_fee,
            'cart_total': order.amount_total,
            'min_order_amount': order.food_restaurant_id.min_order_amount or 0.0,
        }

    @http.route('/food/cart/clear_and_add', type='json', auth="user", website=True)
    def food_cart_clear_and_add(self, product_id, quantity=1, addons=None, combo_items=None, **kwargs):
        order = self._get_cart_order()
        if order:
            order.order_line.sudo().unlink()
            order.sudo().write({
                'food_restaurant_id': False,
                'food_delivery_fee': 0.0,
                'food_delivery_distance': 0.0
            })
        return self.food_cart_add_json(product_id, quantity, addons, combo_items, **kwargs)

    @http.route('/food/cart/get_summary', type='json', auth="user", website=True)
    def food_cart_get_summary(self, **kwargs):
        order = self._get_cart_order()
        if not order:
            return {'cart_quantity': 0, 'cart_total': 0}
        restaurant = order.food_restaurant_id
        summary = self._get_cart_summary_data(order)
        summary['restaurant_id'] = restaurant.id if restaurant else False
        summary['restaurant_url'] = '/food-restaurant/%s' % restaurant.id if restaurant else '/food'
        return summary

    @http.route('/food/order/tip/standalone', type='json', auth="user", website=True)
    def food_order_tip_standalone(self, order_id, amount, **kwargs):
        if amount <= 0:
            return {'error': 'Geçerli bir tutar giriniz.'}
            
        original_order = request.env['sale.order'].sudo().browse(order_id)
        if not original_order.exists():
            return {'error': 'Sipariş bulunamadı.'}
            
        tip_product = request.env.ref('ronix_food_delivery.product_product_tip').sudo()
        
        # Create a new standalone tip order
        tip_order = request.env['sale.order'].sudo().create({
            'partner_id': request.env.user.partner_id.id,
            'food_restaurant_id': original_order.food_restaurant_id.id,
            'note': f"Bahşiş - {original_order.name} referanslı kurye bahşişi",
            'client_order_ref': f"Bahşiş: {original_order.name}",
            'is_food_order': True,
            'is_tip_order': True,
            'original_order_id': original_order.id,
        })
        
        request.env['sale.order.line'].sudo().create({
            'order_id': tip_order.id,
            'product_id': tip_product.id,
            'product_uom_qty': 1.0,
            'price_unit': amount,
            'name': f"Bahşiş ({original_order.name})",
        })

        # Automatic Payment Logic
        user = request.env.user
        is_test_user = user.partner_id.mobile == "+905559999999" or user.partner_id.phone == "+905559999999"
        
        if is_test_user:
            # Test user bypass: directly mark as paid
            tip_order.sudo().write({
                'payment_status': 'paid',
                'state': 'sale',
            })
            success = True
        else:
            # Try to charge the saved card for regular users
            # Calling the existing action_stripe_charge_saved_card method
            intent = tip_order.action_stripe_charge_saved_card()
            success = tip_order.payment_status == 'paid'

        if success:
            # Update the original order's tip amount
            original_order.sudo().write({
                'tip_amount': original_order.tip_amount + amount
            })
            return {
                'success': True,
                'order_name': tip_order.name,
            }
        else:
            # If payment fails, we might want to delete the draft tip order or keep it for manual payment
            # Keeping it as draft for now, but returning error
            return {'error': 'Ödeme başarısız oldu. Lütfen kartınızı kontrol ediniz.'}

    @http.route('/food/cart/update_notes', type='json', auth="user", website=True)
    def food_cart_update_notes(self, notes=None, **kwargs):
        order = self._get_cart_order()
        if order:
            order.sudo().write({'food_order_notes': notes})
            return {'success': True}
        return {'success': False}

    @http.route('/food/cart/apply_coupon', type='http', auth="user", website=True, methods=['POST'])
    def food_cart_apply_coupon(self, promo_code=None, **post):
        order = self._get_cart_order()
        if not order or not promo_code:
            return request.redirect('/food-cart')
            
        # Odoo 16 uses loyalty module with _try_apply_code usually.
        # It may return error messages like {'error': ...} or {'not_found': ...}
        if hasattr(order, '_try_apply_code'):
            status = order.sudo()._try_apply_code(promo_code)
            if isinstance(status, dict):
                if 'not_found' in status:
                    return request.redirect('/food-cart?coupon_error=Kupon kodu geçersiz veya süresi dolmuş.')
                elif 'error' in status:
                    return request.redirect(f'/food-cart?coupon_error={status["error"]}')
                else:
                    # Success dictionary returns dict of {coupon: rewards}
                    reward_successfully_applied = False
                    for coupon, rewards in status.items():
                        # Try to apply the first automatic/unconditional reward we can
                        for reward in rewards:
                            if not reward.multi_product:
                                try:
                                    reward_status = order.sudo()._apply_program_reward(reward, coupon)
                                    if 'error' not in reward_status:
                                        reward_successfully_applied = True
                                        break
                                except Exception:
                                    pass
                        if reward_successfully_applied:
                            break
                            
                    if hasattr(order, '_update_programs_and_rewards'):
                        order.sudo()._update_programs_and_rewards()
                        if hasattr(order, '_auto_apply_rewards'):
                            order.sudo()._auto_apply_rewards()

                    if reward_successfully_applied:
                        return request.redirect('/food-cart?coupon_success=1')
                    else:
                        return request.redirect('/food-cart?coupon_error=Kupon uygulanamadı.')

        elif hasattr(order, 'action_coupon_apply'):
            # Older method fallback maybe
            try:
                pass
            except Exception as e:
                pass
                
        return request.redirect('/food-cart?coupon_success=1')

    @http.route('/food/address/add', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def food_address_add(self, **kwargs):
        partner = request.env.user.partner_id
        
        lat = kwargs.get('lat')
        lng = kwargs.get('lng')
        
        vals = {
            'name': kwargs.get('address_title'),
            'city': kwargs.get('city'),
            'district': kwargs.get('district'),
            'address_details': kwargs.get('address_details'),
            'address_directions': kwargs.get('address_directions'),
            'partner_id': partner.id,
        }
        
        if lat:
            try:
                vals['lat'] = float(lat)
            except ValueError:
                pass
        if lng:
            try:
                vals['lng'] = float(lng)
            except ValueError:
                pass
                
        new_address = request.env['food.delivery.address'].sudo().create(vals)
        
        if not partner.current_food_address_id:
            partner.sudo().write({'current_food_address_id': new_address.id})
            
        if kwargs.get('redirect'):
            return request.redirect(kwargs.get('redirect'))
        return request.redirect('/food-addresses')

    @http.route('/food/address/edit', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def food_address_edit(self, **kwargs):
        address_id = int(kwargs.get('address_id'))
        partner = request.env.user.partner_id
        address = request.env['food.delivery.address'].sudo().browse(address_id)
        if address.exists() and address.partner_id.id == partner.id:
            vals = {
                'name': kwargs.get('address_title'),
                'city': kwargs.get('city'),
                'district': kwargs.get('district'),
                'address_details': kwargs.get('address_details'),
                'address_directions': kwargs.get('address_directions'),
            }
            lat = kwargs.get('lat')
            lng = kwargs.get('lng')
            if lat:
                try: vals['lat'] = float(lat)
                except ValueError: pass
            if lng:
                try: vals['lng'] = float(lng)
                except ValueError: pass
                
            address.sudo().write(vals)
        
        if kwargs.get('redirect'):
            return request.redirect(kwargs.get('redirect'))
        return request.redirect('/food-addresses')

    @http.route('/food/address/select', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def food_address_select(self, **kwargs):
        address_id = int(kwargs.get('address_id'))
        partner = request.env.user.partner_id
        address = request.env['food.delivery.address'].sudo().browse(address_id)
        if address.exists() and address.partner_id.id == partner.id:
            partner.sudo().write({'current_food_address_id': address_id})
            # Sync to current order if any
            order = self._get_cart_order()
            if order:
                order.sudo().write({
                    'food_delivery_address_id': address_id,
                    'food_delivery_address_text': address.address_details,
                })
                order.sudo().action_calculate_delivery_fee()
        return request.redirect('/food-home')

    @http.route('/food/address/delete', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def food_address_delete(self, **kwargs):
        address_id = int(kwargs.get('address_id'))
        partner = request.env.user.partner_id
        address = request.env['food.delivery.address'].sudo().browse(address_id)
        if address.exists() and address.partner_id.id == partner.id:
            if partner.current_food_address_id.id == address_id:
                partner.sudo().write({'current_food_address_id': False})
            address.sudo().unlink()
        return request.redirect('/food-addresses')

    @http.route('/food/address/set_default', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def food_address_set_default(self, **kwargs):
        address_id = int(kwargs.get('address_id'))
        partner = request.env.user.partner_id
        address = request.env['food.delivery.address'].sudo().browse(address_id)
        if address.exists() and address.partner_id.id == partner.id:
            partner.food_address_ids.sudo().write({'is_default': False})
            address.sudo().write({'is_default': True})
            partner.sudo().write({'current_food_address_id': address_id})
        return request.redirect('/food-addresses')
    @http.route('/food/search_suggestions', type='json', auth="user", website=True)
    def search_suggestions(self, query, **kwargs):
        if not query or len(query) < 2:
            return []
            
        suggestions = []
        
        # Search Restaurants
        restaurants = request.env['food.restaurant'].sudo().search([
            ('name', 'ilike', query),
            ('active', '=', True),
            ('is_open', '=', True)
        ], limit=5)
        
        for rest in restaurants:
            suggestions.append({
                'id': rest.id,
                'name': rest.name,
                'type': 'restaurant',
                'url': f'/food-restaurant/{rest.id}',
                'image_url': f'/web/image/food.restaurant/{rest.id}/image_128'
            })
            
        # Search Foods (Limit combined results to 5)
        remaining_slots = 5 - len(suggestions)
        if remaining_slots > 0:
            foods = request.env['product.template'].sudo().search([
                ('name', 'ilike', query),
                ('food_restaurant_id.is_open', '=', True),
                ('food_restaurant_id.is_grocery', '=', False),
                ('is_food', '=', True),
                ('is_published', '=', True)
            ], limit=remaining_slots)
            
            for food in foods:
                suggestions.append({
                    'id': food.id,
                    'name': food.name,
                    'type': 'food',
                    'url': f'/food-restaurant/{food.food_restaurant_id.id}', # Redirect to restaurant page or offcanvas?
                    'food_id': food.id, # To open offcanvas via JS
                    'image_url': f'/web/image/product.template/{food.id}/image_128'
                })
                
        return suggestions[:5]

    @http.route('/food/order/review/save', type='json', auth="user", website=True)
    def food_order_review_save(self, order_id, restaurant_rating, food_rating, restaurant_tags, food_tags, **kwargs):
        order = request.env['sale.order'].sudo().browse(int(order_id))
        if not order.exists() or order.partner_id.id != request.env.user.partner_id.id:
            return {'status': 'error', 'message': 'Sipariş bulunamadı.'}

        if order.has_review:
            return {'status': 'error', 'message': 'Bu sipariş zaten değerlendirilmiş.'}

        # Update Sale Order
        order.write({
            'has_review': True,
            'food_restaurant_rating': str(restaurant_rating),
            'food_rating': str(food_rating),
            'food_restaurant_tag_ids': [(6, 0, [int(t) for t in restaurant_tags])],
            'food_tag_ids': [(6, 0, [int(t) for t in food_tags])],
        })

        # Generate comments from tags
        res_tag_names = request.env['food.review.tag'].sudo().browse([int(t) for t in restaurant_tags]).mapped('name')
        food_tag_names = request.env['food.review.tag'].sudo().browse([int(t) for t in food_tags]).mapped('name')
        
        res_comment = ", ".join(res_tag_names) or "Puan Verildi"
        food_comment = ", ".join(food_tag_names) or "Puan Verildi"

        # Create Restaurant Review
        request.env['food.restaurant.review'].sudo().create({
            'restaurant_id': order.food_restaurant_id.id,
            'order_id': order.id,
            'user_id': request.env.user.id,
            'rating': int(restaurant_rating),
            'food_rating': int(food_rating),
            'tag_ids': [(6, 0, [int(t) for t in restaurant_tags])],
            'comment': res_comment,
        })

        # Create Product Reviews for each item in the order
        for line in order.order_line.filtered(lambda l: l.product_id.is_food):
            request.env['food.product.review'].sudo().create({
                'product_id': line.product_id.product_tmpl_id.id,
                'order_id': order.id,
                'user_id': request.env.user.id,
                'rating': int(food_rating),
                'tag_ids': [(6, 0, [int(t) for t in food_tags])],
                'comment': food_comment,
            })

        return {'status': 'success'}

    @http.route('/food/cart/update_quantity', type='json', auth="user", website=True)
    def food_cart_update_quantity(self, line_id, quantity, **kwargs):
        line = request.env['sale.order.line'].sudo().browse(int(line_id))
        order = self._get_cart_order()

        if not line.exists() or not order or line.order_id.id != order.id:
            return {'error': 'Sipariş satırı bulunamadı.'}

        if quantity <= 0:
            # For combo parent, linked_line_ids will cascade delete
            line.sudo().unlink()
        else:
            line.sudo().write({'product_uom_qty': quantity})
            # Also update linked combo child lines
            if line.product_id.type == 'combo':
                for child in line.linked_line_ids:
                    child.sudo().write({'product_uom_qty': quantity})

        # Ensure delivery fee line and fresh totals
        order.sudo().action_calculate_delivery_fee()
        order.sudo().invalidate_recordset(['amount_untaxed', 'amount_tax', 'amount_total'])

        result = self._get_cart_summary_data(order)
        if line.exists():
            # For combo, total price = sum of child lines
            if line.product_id.type == 'combo':
                result['line_price_total'] = sum(line.linked_line_ids.mapped('price_total'))
            else:
                result['line_price_total'] = line.price_total
        return result

    @http.route('/food/cart/remove_item', type='json', auth="user", website=True)
    def food_cart_remove_item(self, line_id, **kwargs):
        line = request.env['sale.order.line'].sudo().browse(int(line_id))
        order = self._get_cart_order()

        if not line.exists() or not order or line.order_id.id != order.id:
            return {'error': 'Sipariş satırı bulunamadı.'}

        # For combo parent, linked_line_ids cascade delete automatically
        line.sudo().unlink()

        # Ensure delivery fee line and fresh totals
        order.sudo().action_calculate_delivery_fee()
        order.sudo().invalidate_recordset(['amount_untaxed', 'amount_tax', 'amount_total'])

        return self._get_cart_summary_data(order)

    @http.route('/food/payment/manage', type='http', auth="user", website=True)
    def food_payment_manage(self, landing_route='/food-payment-methods', **kwargs):
        from odoo.addons.payment import utils as payment_utils
        partner_sudo = request.env.user.partner_id
        
        availability_report = {}
        providers_sudo = request.env['payment.provider'].sudo()._get_compatible_providers(
            request.env.company.id,
            partner_sudo.id,
            0.,
            force_tokenization=True,
            is_validation=True,
            report=availability_report,
            **kwargs,
        )
        payment_methods_sudo = request.env['payment.method'].sudo()._get_compatible_payment_methods(
            providers_sudo.ids,
            partner_sudo.id,
            force_tokenization=True,
            report=availability_report,
        )
        tokens_sudo = request.env['payment.token'].sudo()._get_available_tokens(
            None, partner_sudo.id, is_validation=True
        )

        access_token = payment_utils.generate_access_token(partner_sudo.id, None, None)
        rendering_context = {
            'providers_sudo': providers_sudo,
            'payment_methods_sudo': payment_methods_sudo,
            'tokens_sudo': tokens_sudo,
            'availability_report': availability_report,
            'reference_prefix': payment_utils.singularize_reference_prefix(prefix='V'),
            'partner_id': partner_sudo.id,
            'access_token': access_token,
            'transaction_route': '/payment/transaction',
            'landing_route': landing_route,
            'mode': 'validation',
            'allow_token_selection': False,
            'allow_token_deletion': True,
        }
        return request.render('ronix_food_delivery.food_payment_manage_page', rendering_context)

    @http.route('/food/payment/set-default/<int:token_id>', type='http', auth='user', website=True, methods=['GET'])
    def food_set_default_card(self, token_id, **kwargs):
        partner = request.env.user.partner_id

        target_token = request.env['payment.token'].sudo().search([
            ('id', '=', token_id),
            ('partner_id', '=', partner.id)
        ])

        if not target_token:
            return request.redirect('/food-payment-methods?error=not_found')

        # Tüm kartlardan varsayılan işaretini kaldır
        all_tokens = request.env['payment.token'].sudo().search([
            ('partner_id', '=', partner.id),
            ('id', '!=', token_id)
        ])
        if all_tokens:
            all_tokens.sudo().write({'default_card': False})

        # Seçilen kartı varsayılan yap
        target_token.sudo().write({'default_card': True})

        return request.redirect('/food-payment-methods?success=default_changed')

    @http.route('/food/payment/delete/<int:token_id>', type='http', auth='user', website=True, methods=['GET'])
    def food_delete_card(self, token_id, **kwargs):
        partner = request.env.user.partner_id

        token = request.env['payment.token'].sudo().search([
            ('id', '=', token_id),
            ('partner_id', '=', partner.id)
        ])

        if not token:
            return request.redirect('/food-payment-methods?error=not_found')

        token.sudo().write({'active': False})
        return request.redirect('/food-payment-methods?success=deleted')
