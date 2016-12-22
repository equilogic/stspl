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
from openerp import fields,models,api

class purchase_order_wiz(models.TransientModel):
    _name = 'purchase.order.wiz'

    supplier_ids = fields.Many2many('res.partner',string='Suppliers')

    @api.multi
    def prepare_po(self,partner,comp):

        sorder = self.env['sale.order'].browse(self._context.get('active_id'))
        po_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        loc_id = self.env['stock.location'].search([('location_id', '!=', False), ('location_id.name', 'ilike', 'WH'),
                    ('company_id.id', '=', comp.id), ('usage', '=', 'internal')])
        
        attn = self.env['res.partner'].search([('parent_id','=',partner.id),('type','=','contact')])
        order_vals = {
          'partner_id': partner.id,
          'invoice_method': 'manual',
          'date_order': sorder.date_order,
          'pricelist_id': partner.property_product_pricelist.id,
          'invoiced':True,
          'currency_id':sorder.currency_id.id,
          'location_id' : loc_id.id or '',
          'incoterm_id':sorder.incoterm.id,
          'payment_term_id':sorder.payment_term.id,
          'attn_pur':attn.ids[0],
          }
        po_res = po_obj.create(order_vals)
        for line in sorder.order_line:
            vals = {
                    'product_id' : line.product_id.id,
                    'name' : line.name,
                    'date_planned':sorder.date_order,
                    'product_qty' : line.product_uom_qty,
                    'product_uom' :line.product_uom.id or False,
                    'price_unit':line.price_unit,
                    'taxes_id': [(6, 0, [x.id for x in line.tax_id])],
                    'price_subtotal':line.price_subtotal,
                    'order_id':po_res.id,
                    }
            po_res1 = po_line_obj.create(vals)

    @api.multi
    def create_po(self):
        cr,uid,context=self.env.args
        com = self.env['res.users'].browse(uid).company_id
        if self.supplier_ids:
            for sup in self.supplier_ids:
                self.prepare_po(sup,com)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: