# -*- coding: utf-8 -*-
import logging
import requests
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_food_order = fields.Boolean(string='Is Food Order', default=False)
    food_restaurant_id = fields.Many2one('food.restaurant', string='Source Restaurant')
    food_delivery_address_id = fields.Many2one('food.delivery.address', string='Technical Address')
    food_delivery_address_text = fields.Char(string='Teslimat Adresi')
    food_customer_name = fields.Char(string='Müşteri Adı')
    food_order_notes = fields.Text(string='Sipariş Notu')
    food_cancel_reason = fields.Text(string='Iptal Sebebi', copy=False, readonly=True)
    food_alert_acknowledged = fields.Boolean(string='Alert Acknowledged', default=False, copy=False)
    has_review = fields.Boolean(string='Has Review', default=False, copy=False)
    food_restaurant_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ], string='Restaurant Rating', default='0')
    food_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ], string='Food Rating', default='0')
    food_restaurant_tag_ids = fields.Many2many('food.review.tag', 'sale_order_restaurant_tag_rel', 'order_id', 'tag_id', string='Restaurant Tags', domain=[('category', '=', 'restaurant')])
    food_tag_ids = fields.Many2many('food.review.tag', 'sale_order_food_tag_rel', 'order_id', 'tag_id', string='Food Tags', domain=[('category', '=', 'product')])

    payment_status = fields.Selection(
        [
            ('not_paid', 'Not Paid'),
            ('paid', 'Paid'),
            ('partial', 'Partial'),
            ('reversed', 'Reversed')
        ],
        string="Payment Status",
        default="not_paid",
        tracking=True,
        copy=False,
    )
    payment_response = fields.Char(string="Payment Response", copy=False)
    payment_try_number = fields.Integer(string="Payment Try Number", copy=False, default=0)

    food_delivery_status = fields.Selection(
        [
            ('preparing', 'Hazırlanıyor'),
            ('on_the_way', 'Yolda'),
            ('delivered', 'Teslim Edildi'),
            ('cancelled', 'İptal Edildi'),
        ],
        string='Teslimat Durumu',
        default='preparing',
        tracking=True,
        copy=False,
    )
    tip_amount = fields.Monetary(string='Bahşiş Tutarı', default=0.0, currency_field='currency_id')
    is_tip_order = fields.Boolean(string='Bahşiş Siparişi mi?', default=False)
    original_order_id = fields.Many2one('sale.order', string='Orijinal Sipariş')
    tip_order_ids = fields.One2many('sale.order', 'original_order_id', string='Bahşiş Siparişleri')
    courier_id = fields.Many2one('res.users', string='Kurye', copy=False)
    preparation_time_start = fields.Datetime(string='Hazırlanma Başlangıcı')
    courier_departed_at = fields.Datetime(string='Kurye Yola Cikti', copy=False, readonly=True)
    delivered_at = fields.Datetime(string='Teslim Edildi Zamani', copy=False, readonly=True)
    food_restaurant_timezone = fields.Selection(related='food_restaurant_id.timezone', string='Restaurant Timezone', readonly=True)
    platform_commission_rate = fields.Float(string='Platform Komisyon Oranı (%)', digits=(16, 2), copy=False)
    platform_commission_amount = fields.Monetary(
        string='Platform Komisyon Tutarı',
        currency_field='currency_id',
        compute='_compute_platform_commission_amount',
        store=True,
        copy=False,
    )
    
    food_delivery_fee = fields.Monetary(string='Teslimat Ücreti', currency_field='currency_id', default=0.0)
    food_delivery_distance = fields.Float(string='Teslimat Mesafesi (km)', digits=(10, 2))

    @api.depends('amount_total', 'platform_commission_rate')
    def _compute_platform_commission_amount(self):
        for order in self:
            order.platform_commission_amount = order.amount_total * (order.platform_commission_rate / 100.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Set preparation time if it's a food order and not a tip order
            is_food = vals.get('is_food_order') or self.env.context.get('default_is_food_order')
            if is_food and not vals.get('is_tip_order'):
                if 'preparation_time_start' not in vals or not vals['preparation_time_start']:
                    vals['preparation_time_start'] = fields.Datetime.now()
            if vals.get('food_restaurant_id') and 'platform_commission_rate' not in vals:
                restaurant = self.env['food.restaurant'].browse(vals['food_restaurant_id'])
                vals['platform_commission_rate'] = restaurant.platform_commission_rate or 0.0
        return super().create(vals_list)

    def write(self, vals):
        if 'food_restaurant_id' in vals and 'platform_commission_rate' not in vals:
            restaurant = self.env['food.restaurant'].browse(vals['food_restaurant_id'])
            vals['platform_commission_rate'] = restaurant.platform_commission_rate or 0.0 if restaurant else 0.0
        status = vals.get('food_delivery_status')
        if status == 'on_the_way' and 'courier_departed_at' not in vals:
            vals['courier_departed_at'] = fields.Datetime.now()
        if status == 'delivered' and 'delivered_at' not in vals:
            vals['delivered_at'] = fields.Datetime.now()
        res = super().write(vals)
        # If status changed to preparing, ensure we have a start time
        if 'food_delivery_status' in vals and vals['food_delivery_status'] == 'preparing':
            for order in self:
                if not order.preparation_time_start:
                    order.sudo().write({'preparation_time_start': fields.Datetime.now()})
        return res

    def action_calculate_delivery_fee(self):
        self.ensure_one()
        _logger.info(f"Ronix Delivery: Calculating fee for order {self.name}")
        
        if not self.is_food_order or not self.food_restaurant_id or not self.food_delivery_address_id:
            _logger.info(f"Ronix Delivery: Skipping, missing required fields. Order: {self.name}, Rest: {self.food_restaurant_id.id}, Addr: {self.food_delivery_address_id.id}")
            return False
            
        # Check if any food lines exist. If not, fee is 0 and we might clear restaurant_id
        food_lines = self.order_line.filtered(lambda l: l.product_id.is_food)
        if not food_lines:
            _logger.info(f"Ronix Delivery: No food lines found for order {self.name}. Setting fee to 0 and removing line.")
            self.sudo().write({
                'food_delivery_fee': 0.0,
                'food_delivery_distance': 0.0,
                'food_restaurant_id': False,
                'platform_commission_rate': 0.0,
            })
            self._update_delivery_fee_line(0.0)
            return True
            
        # Optimization: If fee is already set and not 0, just refresh the line and recompute
        # This avoids redundant Google API calls on every cart update.
        if self.food_delivery_fee > 0.0:
            self._update_delivery_fee_line(self.food_delivery_fee)
            return True

        restaurant = self.food_restaurant_id
        address = self.food_delivery_address_id
        
        company = self.company_id
        api_key = company.x_google_maps_geocode_api_key if hasattr(company, 'x_google_maps_geocode_api_key') else False
        
        # 1. Start with fixed fee if any
        fee = restaurant.delivery_fee or 0.0
        distance_km = 0.0
        
        # 2. Add dynamic fee if base/km prices are set and we have coordinates
        if (restaurant.delivery_base_price or restaurant.delivery_km_price) and api_key:
            if restaurant.latitude and restaurant.longitude and address.lat and address.lng:
                # Google Maps Distance Matrix API
                url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={restaurant.latitude},{restaurant.longitude}&destinations={address.lat},{address.lng}&key={api_key}"
                
                try:
                    _logger.info(f"Ronix Delivery: Calling Distance Matrix API for order {self.name}")
                    response = requests.get(url, timeout=10)
                    data = response.json()
                    if data.get('status') == 'OK':
                        element = data['rows'][0]['elements'][0]
                        if element.get('status') == 'OK':
                            distance_km = element['distance']['value'] / 1000.0
                            self.sudo().write({'food_delivery_distance': distance_km})
                            
                            # Calculate dynamic fee: base + (km_price * distance)
                            fee += restaurant.delivery_base_price + (restaurant.delivery_km_price * distance_km)
                            _logger.info(f"Ronix Delivery: Calculated dynamic fee {fee} for distance {distance_km} km (Order: {self.name})")
                        else:
                            _logger.warning(f"Ronix Delivery: Distance Matrix element status: {element.get('status')} for order {self.name}")
                    else:
                        _logger.warning(f"Ronix Delivery: Distance Matrix status: {data.get('status')} for order {self.name}")
                except Exception as e:
                    _logger.error(f"Ronix Delivery: calculation error for order {self.name}: {str(e)}")
            else:
                _logger.info(f"Ronix Delivery: Missing coordinates. Rest: {restaurant.latitude},{restaurant.longitude}, Addr: {address.lat},{address.lng}")
        
        # Final Fee Application
        self.sudo().write({
            'food_delivery_fee': fee,
            'platform_commission_rate': restaurant.platform_commission_rate or self.platform_commission_rate,
        })
        self._update_delivery_fee_line(fee)
        return True

    def _update_delivery_fee_line(self, fee):
        self.ensure_one()
        delivery_product = self.env.ref('ronix_food_delivery.product_delivery_fee', raise_if_not_found=False)
        if not delivery_product:
            # Fallback to default_code
            delivery_product = self.env['product.product'].sudo().search([('default_code', '=', 'DELIVERY_FEE')], limit=1)
            
        if not delivery_product:
            return
            
        # Find if line already exists
        delivery_line = self.order_line.filtered(lambda l: l.product_id.id == delivery_product.id)
        
        if fee <= 0.0:
            if delivery_line:
                delivery_line.sudo().unlink()
                _logger.info(f"Ronix Delivery: Removed delivery fee line for order {self.name}")
            return

        if delivery_line:
            delivery_line.sudo().write({
                'price_unit': fee,
                'product_uom_qty': 1.0,
            })
        else:
            self.sudo().write({
                'order_line': [(0, 0, {
                    'product_id': delivery_product.id,
                    'product_uom_qty': 1.0,
                    'price_unit': fee,
                    'name': 'Teslimat Ücreti',
                    'sequence': 999,
                })]
            })
        
        # The write above triggers recompute of amount_total
        pass

    def action_stripe_charge_saved_card(self):
        self = self.sudo().ensure_one()
        import requests
        import json
        import logging
        _logger = logging.getLogger(__name__)

        full_log = []
        intent = None

        if self.payment_try_number > 5:
            full_log.append("Order try many times error")
            return False

        full_log.append(f"Processing payment for order: {self.name}")
    
        try:
            tokens = self.env['payment.token'].sudo().search([
                ('partner_id', '=', self.partner_id.id),
                ('provider_id.code', '=', 'stripe'),
            ])
            
            # Ensure at least one default card
            if not tokens.filtered(lambda t: t.default_card) and tokens:
                tokens[0].sudo().write({'default_card': True})

            token = self.env['payment.token'].sudo().search([
                ('partner_id', '=', self.partner_id.id),
                ('provider_id.code', '=', 'stripe'),
                ('default_card', '=', True),
            ], limit=1)

            if not token:
                full_log.append("No Stripe payment token found for this partner.")
                self.write({
                    'payment_status': 'not_paid',
                    'payment_try_number': self.payment_try_number + 1,
                    'payment_response': "\n".join(full_log),
                })
                self.message_post(body="\n".join(full_log))
                return False

            provider = token.provider_id
            secret_key = getattr(provider, 'stripe_secret_key', False)

            if not secret_key:
                full_log.append("Stripe Secret Key is missing on provider.")
                self.write({
                    'payment_status': 'not_paid',
                    'payment_try_number': self.payment_try_number + 1,
                    'payment_response': "\n".join(full_log),
                })
                self.message_post(body="\n".join(full_log))
                return False

            customer_id = token.provider_ref
            payment_method_id = getattr(token, 'stripe_payment_method', False)

            if not payment_method_id:
                try:
                    pm_resp = requests.get(
                        "https://api.stripe.com/v1/payment_methods",
                        params={"customer": customer_id, "type": "card"},
                        headers={"Authorization": f"Bearer {secret_key}"},
                        timeout=10,
                    )
                    pm_data = pm_resp.json()
                    payment_method_id = pm_data.get('data', [{}])[0].get('id', False)
                except Exception as e:
                    full_log.append(f"Stripe error while fetching payment methods: {str(e)}")
                    self.write({
                        'payment_status': 'not_paid',
                        'payment_try_number': self.payment_try_number + 1,
                        'payment_response': "\n".join(full_log),
                    })
                    return False

            if not payment_method_id:
                full_log.append("Stripe: No saved card found.")
                self.write({'payment_status': 'not_paid', 'payment_response': "\n".join(full_log)})
                return False

            # Amount in cents
            decimals = self.currency_id.decimal_places or 2
            amount_int = int(round(self.amount_total * (10 ** decimals)))

            # Create PaymentIntent
            try:
                response = requests.post(
                    "https://api.stripe.com/v1/payment_intents",
                    data={
                        "amount": amount_int,
                        "currency": self.currency_id.name.lower(),
                        "customer": customer_id,
                        "payment_method": payment_method_id,
                        "off_session": "true",
                        "confirm": "true",
                    },
                    headers={"Authorization": f"Bearer {secret_key}"},
                    timeout=15,
                )
                intent = response.json()
            except Exception as e:
                full_log.append(f"Stripe PaymentIntent error: {str(e)}")
                self.write({'payment_status': 'not_paid', 'payment_response': "\n".join(full_log)})
                return False

            status = intent.get("status")
            if status == "succeeded":
                # Create PaymentTransaction in Odoo
                try:
                    self.env["payment.transaction"].sudo().create({
                        "amount": self.amount_total,
                        "currency_id": self.currency_id.id,
                        "partner_id": self.partner_id.id,
                        "provider_id": provider.id,
                        "reference": f"{self.name}-{fields.Datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "provider_reference": intent.get("id"),
                        "token_id": token.id,
                        "state": "done",
                    })
                    self.write({'payment_status': 'paid'})
                    self.action_confirm() # Confirm the order
                    full_log.append("Payment successful and order confirmed.")
                except Exception as e_tx:
                    full_log.append(f"Odoo transaction creation failed: {str(e_tx)}")
                    _logger.exception("Odoo transaction creation failed")
            else:
                error_msg = intent.get("last_payment_error", {}).get("message", "Payment failed")
                full_log.append(f"Stripe status: {status}. Error: {error_msg}")
                self.write({'payment_status': 'not_paid'})

            self.write({
                'payment_try_number': self.payment_try_number + 1,
                'payment_response': json.dumps(intent) if intent else "\n".join(full_log),
            })
            self.message_post(body="\n".join(full_log))
            return intent

        except Exception as e:
            _logger.exception("Unexpected error in Stripe charge")
            return False

    def action_food_mark_on_the_way(self):
        for record in self:
            if record.state in ['draft', 'sent']:
                record.action_confirm()  # Ensure order is confirmed when it goes on the way
            record.write({'food_delivery_status': 'on_the_way'})

    def action_food_mark_delivered(self):
        for record in self:
            record.write({'food_delivery_status': 'delivered'})

    def action_food_cancel(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Siparis Iptal',
            'res_model': 'food.order.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
            },
        }

    def action_process_food_cancel(self, cancel_reason):
        import requests
        import logging
        _logger = logging.getLogger(__name__)

        for record in self:
            test_user = (
                record.partner_id.mobile == "+905559999999"
                or record.partner_id.phone == "+905559999999"
                or record.partner_id.user_ids.filtered(lambda u: u.login == '+905559999999')
            )

            # First, check if there's a successful Stripe payment to refund
            if record.payment_status == 'paid':
                try:
                    if test_user:
                        record.payment_status = 'reversed'
                        record.message_post(body="Test kullanicisi icin iade edilmis gibi isaretlendi.")
                    else:
                        # Find the successful transaction to get the provider reference
                        tx = self.env['payment.transaction'].sudo().search([
                            ('reference', 'ilike', record.name),
                            ('state', '=', 'done'),
                            ('provider_id.code', '=', 'stripe')
                        ], limit=1, order='id desc')

                        if tx and tx.provider_reference:
                            provider = tx.provider_id
                            secret_key = getattr(provider, 'stripe_secret_key', False)
                            if secret_key:
                                response = requests.post(
                                    "https://api.stripe.com/v1/refunds",
                                    data={"payment_intent": tx.provider_reference},
                                    headers={"Authorization": f"Bearer {secret_key}"},
                                    timeout=15
                                )
                                refund_data = response.json()
                                if response.status_code == 200 and refund_data.get('status') == 'succeeded':
                                    record.payment_status = 'reversed'
                                    record.message_post(body="Odeme Stripe uzerinden basariyla iade edildi.")
                                else:
                                    error_msg = refund_data.get("error", {}).get("message", "Bilinmeyen hata")
                                    record.message_post(body=f"Stripe iade hatasi: {error_msg}")
                        else:
                            record.message_post(body="Iade yapilacak basarili bir Stripe islemi bulunamadi.")
                except Exception as e:
                    _logger.exception("Stripe refund failed")
                    record.message_post(body=f"Stripe iade istegi sirasinda bir hata olustu: {str(e)}")

            # Cancel the order itself
            record.write({
                'food_delivery_status': 'cancelled',
                'food_cancel_reason': cancel_reason,
            })
            record.message_post(body=f"Siparis iptal sebebi: {cancel_reason}")
            record.action_cancel()

    def action_open_google_maps(self):
        self.ensure_one()
        if self.food_delivery_address_id and self.food_delivery_address_id.lat and self.food_delivery_address_id.lng:
            url = f"https://www.google.com/maps/search/?api=1&query={self.food_delivery_address_id.lat},{self.food_delivery_address_id.lng}"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Hata',
                'message': 'Bu adresin koordinat bilgisi bulunamadı.',
                'sticky': False,
            }
        }
