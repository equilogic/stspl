# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Serpent Consulting Services Pvt. Ltd.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models,fields,api
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = 'account.invoice'


    amount_discount = fields.Float(string="Discount",digits=dp.get_precision('Account'),store=True, readonly=True,
                        compute='_compute_amount')

    @api.one
    @api.depends('invoice_line.discount','invoice_line.quantity')
    def _compute_amount(self):
        res = super(account_invoice,self)._compute_amount()
        self.amount_discount = sum(line.discount * line.quantity for line in self.invoice_line) 
        return res


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    discount_type = fields.Selection([('percent', 'Percentage'),('amount', 'Amount')],'Discount Type',default='percent')


    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id','discount_type')
    def _compute_price(self):
        res = super(account_invoice_line,self)._compute_price()
        if self.discount_type == 'percent':
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        elif self.discount_type == 'amount':    
            price = self.price_unit - self.discount or 0.0
            taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
            self.price_subtotal = taxes['total']
            if self.invoice_id:
                self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
        return res
        

