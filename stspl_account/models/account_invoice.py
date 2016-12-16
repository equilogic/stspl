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

from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp import models,fields,api


class account_invoice(models.Model):
    
    _inherit = 'account.invoice'

    purchase_id= fields.Many2one('purchase.order','Purchase')
    sales_id=fields.Many2one('sale.order','Sales')
    customer_po = fields.Char('Customer PO')
    attn_inv = fields.Many2one('res.partner', 'ATTN')
    ship_via_id = fields.Many2one('ship.via', 'Ship Via')


    @api.multi
    def invoice_validate(self):
        prefix = ''
        cr,uid,context = self.env.args
        if self.partner_id and self.number:
            country = self.partner_id.country_id.name
            currency = self.currency_id.name
            if self.type=='out_invoice':
                next_id = self.env['ir.sequence'].get('account.invoice.customer')
                self.write({'number': next_id})                
            if self.type=='in_invoice':
                next_supp_id = self.env['ir.sequence'].get('account.invoice.supplier')
                self.write({'number': next_supp_id})                      
        return self.write({'state': 'open'})

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    def _prepare_invoice(self,cr,uid,order, line_ids,context=None):
        res = super(purchase_order, self)._prepare_invoice(cr,uid,order, line_ids,context=context)
        res.update({'purchase_id':order.id})
        return  res
    
    
class sale_order(models.Model):
    _inherit='sale.order'

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        res=super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context=context)
        res.update({'sales_id':order.id})
        return res

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
                        report_dict.update({'display_name': 'Quotation Acknowledgment','name': 'Quotation Acknowledgment',
                                            'string': 'Quotation Acknowledgment'})
                    if action_rec.name == 'Quotations' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'stspl_account.report_stspl_proforma_invoice':
                        report_dict.update({'display_name': 'Quotation Proforma Invoice','name': 'Quotation Proforma Invoice',
                                            'string': 'Quotation Proforma Invoice'})
        return result

