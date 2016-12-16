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


class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    customer_po = fields.Char('Customer PO')
    attn_pur = fields.Many2one('res.partner', 'ATTN')
    ship_via_id = fields.Many2one('ship.via', 'Ship Via')  

    @api.model
    def create(self,vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('purchase.order.new')
        res = super(purchase_order,self).create(vals)
        return res
        
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        '''
        Override this method to Rename Report name to print from Quatation and Purchase order menu.
        '''
        action_obj = self.env['ir.actions.actions']
        result = super(purchase_order, self).fields_view_get(view_id, 
            view_type, toolbar=toolbar, submenu=submenu)
        cr,uid,context = self.env.args
        if toolbar and context.get('params', False) and context['params'].get('action', False):
            action_rec = action_obj.browse(context['params']['action'])
            if result.get('toolbar', False) and result['toolbar'].get('print', False):
                for report_dict in result['toolbar']['print']:
                    if action_rec.name == 'Requests for Quotation' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'purchase.report_purchaseorder':
                        report_dict.update({'display_name': 'Quotation Order','name': 'Quotation Order',
                                            'string': 'Quotation Order'})
                    if action_rec.name == 'Requests for Quotation' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'stspl_purchase.report_purchase_order':
                        report_dict.update({'display_name': 'Quotation Report','name': 'Quotation Report',
                                            'string': 'Quotation Report'})
                    if action_rec.name == 'Purchase Orders' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'purchase.report_purchasequotation':
                        report_dict.update({'display_name': 'Request for Purchase','name': 'Request for Purchase',
                                            'string': 'Request for Purchase'})
        return result
    



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: