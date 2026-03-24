# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PosRefundWizard(models.TransientModel):
    _name = 'pos.refund.wizard'
    _description = 'POS İade Sihirbazı'

    # İlişkiler
    transaction_id = fields.Many2one('payment.transaction', string='İşlem', required=True)
    provider_id = fields.Many2one(related='transaction_id.provider_id', string='Sağlayıcı')
    
    # Tutar Bilgileri
    original_amount = fields.Monetary(related='transaction_id.amount', string='Orijinal Tutar')
    already_refunded = fields.Monetary(related='transaction_id.refund_amount', string='Önceki İadeler')
    max_amount = fields.Monetary(string='Maksimum İade Tutarı', compute='_compute_max_amount')
    refund_amount = fields.Monetary(string='İade Tutarı', required=True)
    
    # Para Birimi
    currency_id = fields.Many2one(related='transaction_id.currency_id', string='Para Birimi')
    
    # İade Nedeni
    refund_reason = fields.Selection([
        ('customer_request', 'Müşteri Talebi'),
        ('duplicate_charge', 'Çift Tahsilat'),
        ('fraud', 'Dolandırıcılık'),
        ('product_return', 'Ürün İadesi'),
        ('service_issue', 'Hizmet Sorunu'),
        ('other', 'Diğer'),
    ], string='İade Nedeni', required=True, default='customer_request')
    
    refund_note = fields.Text(string='İade Notu')
    
    # Onay
    confirm_refund = fields.Boolean(string='İadeyi Onaylıyorum', default=False)

    # ==================== HESAPLAMA METOTLARI ====================
    
    @api.depends('original_amount', 'already_refunded')
    def _compute_max_amount(self):
        for wizard in self:
            wizard.max_amount = wizard.original_amount - wizard.already_refunded

    # ==================== KISITLAMALAR ====================
    
    @api.constrains('refund_amount', 'max_amount')
    def _check_refund_amount(self):
        for wizard in self:
            if wizard.refund_amount <= 0:
                raise ValidationError(_('İade tutarı sıfırdan büyük olmalıdır.'))
            if wizard.refund_amount > wizard.max_amount:
                raise ValidationError(_('İade tutarı maksimum tutardan büyük olamaz.'))

    # ==================== İŞ METOTLARI ====================
    
    def action_confirm_refund(self):
        """İade işlemini onaylar"""
        self.ensure_one()
        
        if not self.confirm_refund:
            raise ValidationError(_('Lütfen iadeyi onaylayın.'))
        
        # İade işlemini gerçekleştir
        result = self.transaction_id.action_refund(self.refund_amount)
        
        # İade notunu kaydet
        if self.refund_note:
            self.transaction_id.message_post(
                body=_('İade Notu: %s') % self.refund_note
            )
        
        return result


class PosCancelWizard(models.TransientModel):
    _name = 'pos.cancel.wizard'
    _description = 'POS İptal Sihirbazı'

    # İlişkiler
    transaction_id = fields.Many2one('payment.transaction', string='İşlem', required=True)
    provider_id = fields.Many2one(related='transaction_id.provider_id', string='Sağlayıcı')
    
    # İşlem Bilgileri
    order_id = fields.Char(related='transaction_id.pos_order_id', string='Sipariş ID')
    amount = fields.Monetary(related='transaction_id.amount', string='Tutar')
    currency_id = fields.Many2one(related='transaction_id.currency_id', string='Para Birimi')
    payment_date = fields.Datetime(related='transaction_id.payment_date', string='Ödeme Tarihi')
    
    # İptal Nedeni
    cancel_reason = fields.Selection([
        ('customer_request', 'Müşteri Talebi'),
        ('technical_error', 'Teknik Hata'),
        ('duplicate_transaction', 'Çift İşlem'),
        ('fraud_suspected', 'Dolandırıcılık Şüphesi'),
        ('order_cancelled', 'Sipariş İptali'),
        ('other', 'Diğer'),
    ], string='İptal Nedeni', required=True, default='customer_request')
    
    cancel_note = fields.Text(string='İptal Notu')
    
    # Onay
    confirm_cancel = fields.Boolean(string='İptali Onaylıyorum', default=False)
    
    # Uyarı
    warning_message = fields.Text(string='Uyarı', compute='_compute_warning_message')

    # ==================== HESAPLAMA METOTLARI ====================
    
    @api.depends('payment_date')
    def _compute_warning_message(self):
        for wizard in self:
            if wizard.payment_date:
                from datetime import datetime, timedelta
                days_passed = (datetime.now() - wizard.payment_date).days
                if days_passed > 1:
                    wizard.warning_message = _(
                        'UYARI: Bu işlem üzerinden %s gün geçmiş. '
                        'İptal yerine iade işlemi yapmanız önerilir.'
                    ) % days_passed
                else:
                    wizard.warning_message = False
            else:
                wizard.warning_message = False

    # ==================== İŞ METOTLARI ====================
    
    def action_confirm_cancel(self):
        """İptal işlemini onaylar"""
        self.ensure_one()
        
        if not self.confirm_cancel:
            raise ValidationError(_('Lütfen iptali onaylayın.'))
        
        # İptal işlemini gerçekleştir
        result = self.transaction_id.action_cancel_transaction()
        
        # İptal notunu kaydet
        if self.cancel_note:
            self.transaction_id.message_post(
                body=_('İptal Notu: %s') % self.cancel_note
            )
        
        return result


class PosStatusQueryWizard(models.TransientModel):
    _name = 'pos.status.query.wizard'
    _description = 'POS Durum Sorgulama Sihirbazı'

    # Sorgu Tipi
    query_type = fields.Selection([
        ('transaction', 'İşlem ID ile'),
        ('order', 'Sipariş ID ile'),
        ('date_range', 'Tarih Aralığı ile'),
    ], string='Sorgu Tipi', required=True, default='transaction')
    
    # İşlem ID ile sorgu
    transaction_id = fields.Many2one('payment.transaction', string='İşlem')
    
    # Sipariş ID ile sorgu
    order_id = fields.Char(string='Sipariş ID')
    
    # Tarih aralığı ile sorgu
    date_from = fields.Date(string='Başlangıç Tarihi')
    date_to = fields.Date(string='Bitiş Tarihi')
    provider_id = fields.Many2one('payment.provider', string='Sağlayıcı')
    
    # Sonuçlar
    result_ids = fields.Many2many('payment.transaction', string='Sonuçlar', compute='_compute_results')
    result_count = fields.Integer(string='Sonuç Sayısı', compute='_compute_results')

    # ==================== HESAPLAMA METOTLARI ====================
    
    @api.depends('query_type', 'transaction_id', 'order_id', 'date_from', 'date_to', 'provider_id')
    def _compute_results(self):
        for wizard in self:
            domain = []
            
            if wizard.query_type == 'transaction' and wizard.transaction_id:
                domain.append(('id', '=', wizard.transaction_id.id))
            elif wizard.query_type == 'order' and wizard.order_id:
                domain.append(('pos_order_id', 'ilike', wizard.order_id))
            elif wizard.query_type == 'date_range':
                if wizard.date_from:
                    domain.append(('payment_date', '>=', wizard.date_from))
                if wizard.date_to:
                    domain.append(('payment_date', '<=', wizard.date_to))
                if wizard.provider_id:
                    domain.append(('provider_id', '=', wizard.provider_id.id))
            
            if domain:
                transactions = self.env['payment.transaction'].search(domain)
                wizard.result_ids = [(6, 0, transactions.ids)]
                wizard.result_count = len(transactions)
            else:
                wizard.result_ids = [(5, 0, 0)]
                wizard.result_count = 0

    # ==================== İŞ METOTLARI ====================
    
    def action_query(self):
        """Sorguyu çalıştırır"""
        self.ensure_one()
        
        if self.query_type == 'transaction' and self.transaction_id:
            # Tek işlem sorgula
            result = self.transaction_id.action_query_status()
            return result
        
        elif self.result_ids:
            # Sonuçları göster
            return {
                'name': _('Sorgu Sonuçları'),
                'type': 'ir.actions.act_window',
                'res_model': 'payment.transaction',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.result_ids.ids)],
            }
        
        return {'type': 'ir.actions.act_window_close'}
