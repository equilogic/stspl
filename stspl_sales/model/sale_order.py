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

 
class shipment_term(models.Model):
    _name = 'shipment.term'
    
    name = fields.Char('Name') 
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: