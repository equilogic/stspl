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
import time
from openerp.osv import fields, osv
from openerp import models,fields,api
from openerp.tools.translate import _
from openerp.exceptions import except_orm, ValidationError
import openerp.addons.decimal_precision as dp

class sale_order(models.Model):
    _inherit='sale.order'

    # discount_type = fields.Selection([('percent', 'Percentage'),('amount', 'Amount')],'Discount Type', readonly=True,
    #                         states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
    # discount_rate = fields.Float('Discount Rate',digits_compute=dp.get_precision('Account'), readonly=True,
    #                         states={'draft': [('readonly', False)], 'open': [('readonly', False)]})


    discount_type = fields.Selection([('percent', 'Percentage'),('amount', 'Amount')],'Discount Type')
    discount_rate = fields.Float('Discount Rate',digits_compute=dp.get_precision('Account'))



from openerp.osv import fields, osv
class sale_order(osv.osv):

    _inherit = 'sale.order'

    @api.onchange('discount_type', 'discount_rate')
    def supply_rate(self):
        disc_amnt=0.0
        total=0.0
        for so in self:
            if so.discount_rate != 0:
                if so.discount_type == 'percent':
                    disc_amnt = (self.amount_untaxed * so.discount_rate) / 100
                else:
                    disc_amnt = so.discount_rate * 1
            self.amount_discount =disc_amnt
            total = (so.amount_untaxed+so.amount_tax) - disc_amnt
            self.amount_total = total


    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

   
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        total=0.0
        discount=0.0
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                 'amount_untaxed': 0.0,
                 'amount_tax': 0.0,
                 'amount_total': 0.0,
                 'amount_discount':0.0,
            }
            val = val1 =val2= 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                 val1 += line.price_subtotal
                 val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            if order.discount_rate != 0:
                if order.discount_type == 'percent':
                    discount = (res[order.id]['amount_untaxed']*order.discount_rate) / 100.0
                else:
                    discount = order.discount_rate
            res[order.id]['amount_discount'] = discount
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']-res[order.id]['amount_discount']
        return res

    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
                
            'amount_untaxed': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                             string='Untaxed Amount',
                            store={'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','discount_type', 'discount_rate'], 10),
                                   'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10)},
                            multi='sums', help="The amount without tax.", track_visibility='always'),
            'amount_tax': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                         string='Taxes',
                         store={'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','discount_type', 'discount_rate'], 10),
                                'sale.order.line': (_get_order,
                             ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10), },
                         multi='sums', help="The tax amount."),
            'amount_total': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                            string='Total',
                            store={
                            'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','discount_type', 'discount_rate'], 10),
                            'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                            },
                            multi='sums', help="The total amount."),
            'amount_discount' : fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Purchase Price'), string='Discount',
                            multi="sums", help="The total discount amount",
                            store={'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','discount_type', 'discount_rate'], 10),
                                   'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10)},
                            ),
                
                }

    
    @api.multi
    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self, pricelist_id, order_lines):
        res = super(sale_order, self).onchange_pricelist_id(pricelist_id, order_lines)
        cur_lst = []
        
        price_list_rec = self.env['product.pricelist'].browse(pricelist_id)
        if price_list_rec.currency_id:
            curr = price_list_rec.currency_id
            if res and res.get('value', False):
                res['value'].update({'currency_rate': price_list_rec.currency_id.rate_silent or 0.0})
            else:
                res.update({'value': {'currency_rate': price_list_rec.currency_id.rate_silent or 0.0}})
        if self.partner_id and not self.partner_id.currency:
            raise except_orm(_('Error!'), _('PLease select Currency for Customer'))
        if self.pricelist_id and self.partner_id and self.partner_id.currency:
            for cur in self.partner_id.currency:
                cur_lst.append(cur.id)

            if self.pricelist_id.currency_id.id not in cur_lst:
                raise except_orm(_('Error!'), _('Customer Currency and Selected Currency are not Match'))
        return res

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self, part):
        res = super(sale_order, self).onchange_partner_id(part)

        if part:
            partner_data = self.env['res.partner'].browse(part)
            if partner_data and partner_data.country_id:
                price_list_ids = self.env['product.pricelist'].search([('currency_id', '=', partner_data.country_id and partner_data.country_id.currency_id.id)])
                if price_list_ids:
                    res['value']['pricelist_id'] = price_list_ids.ids
            else:
                res['value']['pricelist_id'] = partner_data.property_product_pricelist.id
        return res
    
   
    @api.model
    def _prepare_invoice(self, order, lines):
        res = super(sale_order, self)._prepare_invoice(order, lines)
        res.update({'invoice_from_sale':True,
                    'partner_id':order.partner_id.id,
                    'part_inv_id':order.partner_invoice_id.id,
                    'part_ship_id':order.partner_shipping_id.id,
                    'attn_inv':order.attn_sal.id,
                    'discount_type':order.discount_type,
                    'discount_rate':order.discount_rate,
                    'amount_discount':order.amount_discount,
                    })
        return res

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = 'sale.advance.payment.inv'
    
    @api.multi
    def _prepare_advance_invoice_vals(self):
        res = super(sale_advance_payment_inv, self)._prepare_advance_invoice_vals()
        sale = self.env['sale.order'].browse(self._context.get('active_id'))
        for val in res:
            val[1].update({'invoice_from_sale':True,
                           'partner_id':sale.partner_id.id,
                           'part_inv_id':sale.partner_invoice_id.id,
                           'part_ship_id':sale.partner_shipping_id.id,
                           'attn_inv':sale.attn_sal.id,
                           'discount_type':sale.discount_type,
                           'discount_rate':sale.discount_rate,
                           'amount_discount':sale.amount_discount,
                           })
        return res