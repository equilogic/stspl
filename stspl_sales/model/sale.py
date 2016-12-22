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
from openerp.osv import fields, osv


class sale_order(osv.osv):
    _inherit = 'sale.order'

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
            tot_dicount = 0.0
            for line in order.order_line:
                 actual_amt = line.product_uom_qty * line.price_unit
                 tot_dicount += (actual_amt - line.price_subtotal)
                 val1 += line.price_subtotal
                 val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_discount'] = tot_dicount
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
            'amount_discount' : fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Purchase Price'), string='Discount',
                            multi="sums", help="The total discount amount",
                            store={'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                   'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10)})
     }

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'discount_type' : fields.selection([('percent', 'Percentage'),('amount', 'Amount')], 'Discount Type')
    }

    _defaults = {
                'discount_type': 'percent'
    }

    def _calc_line_base_price(self, cr, uid, line, context=None):
        if line.discount_type == 'percent':
            print "\n PERCENT ::::::::::::", line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            return line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        elif line.discount_type == 'amount':
            print "\n AMOUNT BASED ::::::::::::::", line.price_unit - line.discount or 0.0
            return line.price_unit - line.discount or 0.0
        else:
            return line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: