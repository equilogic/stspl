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
from openerp import models,fields,api
from openerp.tools.translate import _
from openerp.exceptions import except_orm, ValidationError


class sale_order(models.Model):
    _inherit='sale.order'

    customer_po = fields.Char('Customer PO')
    attn_sales = fields.Many2one('res.partner', 'ATTN')
    ship_via_id = fields.Many2one('ship.via', 'Ship Via')
    is_po = fields.Boolean('Is PO',default=False)
    purchase_ids = fields.One2many('purchase.order','sale_id','Purchase Order')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        '''
        Override this method to Rename Report name to print from Quatation and Sales order menu.
        '''
        action_obj = self.env['ir.actions.actions']
        result = super(sale_order, self).fields_view_get(view_id, 
            view_type, toolbar=toolbar, submenu=submenu)
        cr,uid,context = self.env.args
        if toolbar and context.get('params', False) and context['params'].get('action', False):
            action_rec = action_obj.browse(context['params']['action'])
            if result.get('toolbar', False) and result['toolbar'].get('print', False):
                for report_dict in result['toolbar']['print']:
                    if action_rec.name == 'Quotations' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'stspl_sales.report_sale_order':
                        report_dict.update({'display_name': 'Quotation','name': 'Quotation',
                                            'string': 'Quotation'})
                    if action_rec.name == 'Quotations' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'stspl_account.report_sale_acknowledgment':
                        report_dict.update({'display_name': '','name': '',
                                            'string': ''})
                    if action_rec.name == 'Quotations' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'stspl_account.report_stspl_proforma_invoice':
                        report_dict.update({'display_name': '','name': '',
                                            'string': ''})
                                                
                    if action_rec.name == 'Sales Orders' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'stspl_account.report_sale_acknowledgment':
                        report_dict.update({'display_name': 'Acknowledgment','name': 'Acknowledgment',
                                            'string': 'Acknowledgment'})
                    if action_rec.name == 'Sales Orders' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'stspl_account.report_stspl_proforma_invoice':
                        report_dict.update({'display_name': 'Proforma Invoice','name': 'Proforma Invoice',
                                            'string': 'Proforma Invoice'})
        return result


    @api.model
    def create(self,vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('sale.order.new')
        res = super(sale_order,self).create(vals)
        return res
    
    @api.multi
    def write(self,vals):
        res = super(sale_order,self).write(vals)
        for sale_rec in self:
            sale_rec.update_related_rfq(vals)
        return res
    
    @api.multi
    def update_related_rfq(self, vals):
        sale_l_obj = self.env['sale.order.line']
        purch_obj = self.env['purchase.order']
        purch_l_obj = self.env['purchase.order.line']
        if vals:
            for sale_rec in self:
                if sale_rec.purchase_ids:
                    purchase_vals = {}
                    if vals.get('date_order',False):
                        purchase_vals.update({'date_order': vals.get('date_order')})
                    if vals.get('pricelist_id',False):
                        purchase_vals.update({'pricelist_id': vals.get('pricelist_id')})
                    if vals.get('currency_id',False):
                        purchase_vals.update({'currency_id': vals.get('currency_id')})
                    if vals.get('incoterm',False):
                        purchase_vals.update({'incoterm_id': vals.get('incoterm')})
                    if vals.get('payment_term',False):
                        purchase_vals.update({'payment_term_id': vals.get('payment_term')})
                    if vals.get('customer_po',False):
                        purchase_vals.update({'customer_po': vals.get('customer_po')})
                    if purchase_vals:
                        sale_rec.purchase_ids.write(purchase_vals)
                if vals.get('order_line', False):
                    for p in sale_rec.purchase_ids:
                        for s_line_val in vals['order_line']:
                            if s_line_val and s_line_val[1] and s_line_val[2]:
                                purch_line_vals={}
                                purch_lines = purch_l_obj.search([('so_line','=', s_line_val[1])])
                                if purch_lines:
                                    if s_line_val[2].get('product_id',False):
                                        purch_line_vals.update({'product_id': s_line_val[2].get('product_id')})
                                    if s_line_val[2].get('name',False):
                                        purch_line_vals.update({'name': s_line_val[2].get('name')})
                                    if s_line_val[2].get('product_uom_qty',False):
                                        purch_line_vals.update({'product_qty': s_line_val[2].get('product_uom_qty')})
                                    if s_line_val[2].get('product_uom',False):
                                        purch_line_vals.update({'product_uom': s_line_val[2].get('product_uom')})
                                    if s_line_val[2].get('price_unit',False):
                                        purch_line_vals.update({'price_unit': s_line_val[2].get('price_unit')})
                                    if s_line_val[2].get('price_subtotal',False):
                                        purch_line_vals.update({'price_subtotal': s_line_val[2].get('price_subtotal')})
                                    purch_lines.write(purch_line_vals)
                            elif s_line_val and s_line_val[2] and not s_line_val[1]:
                                new_sale_id = sale_l_obj.search([('product_id','=', s_line_val[2].get('product_id', False)),
                                                   ('product_uom_qty','=', s_line_val[2].get('product_uom_qty', False)),
                                                   ('price_unit','=', s_line_val[2].get('price_unit', False)),
                                                   ('order_id','=', sale_rec.id)])
                                purch_line_vals = {}
                                if new_sale_id and s_line_val[2]:
                                    purch_line_vals.update({'order_id': p.id, 'date_planned': p.date_order or datetime.now().date() or False})
                                    if s_line_val[2].get('product_id',False):
                                        purch_line_vals.update({'product_id': s_line_val[2].get('product_id')})
                                    if s_line_val[2].get('name',False):
                                        purch_line_vals.update({'name': s_line_val[2].get('name')})
                                    if s_line_val[2].get('product_uom_qty',False):
                                        purch_line_vals.update({'product_qty': s_line_val[2].get('product_uom_qty')})
                                    if s_line_val[2].get('product_uom',False):
                                        purch_line_vals.update({'product_uom': s_line_val[2].get('product_uom')})
                                    if s_line_val[2].get('price_unit',False):
                                        purch_line_vals.update({'price_unit': s_line_val[2].get('price_unit')})
                                    if s_line_val[2].get('price_subtotal',False):
                                        purch_line_vals.update({'price_subtotal': s_line_val[2].get('price_subtotal')})
                                    if s_line_val[2].get('tax_id',False):
                                        purch_line_vals.update({'taxes_id':  [(6, 0, [x.id for x in p.order_line[-1].taxes_id])]})
                                    purch_line_vals.update({'so_line': new_sale_id.ids[0] or False})
                                    
                                new_purch_line_id = purch_l_obj.create(purch_line_vals)
        return True
class sale_order_line(models.Model):
    _inherit='sale.order.line'
    
    @api.multi
    def unlink(self):
        purch_lines = self.env['purchase.order.line'].search([('so_line','=',self.id )])
        if purch_lines:
            purch_lines.unlink()
        return super(sale_order_line, self).unlink()

class shipment_term(models.Model):
    _name = 'shipment.term'
    
    name = fields.Char('Name') 
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: