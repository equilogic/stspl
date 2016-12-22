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
from openerp import models,fields,api, _


class account_invoice(models.Model):
    
    _inherit = 'account.invoice'

    purchase_id= fields.Many2one('purchase.order','Purchase')
    sales_id=fields.Many2one('sale.order','Sales')
    customer_po = fields.Char('Customer PO')
    attn_inv = fields.Many2one('res.partner', 'ATTN')
    ship_via_id = fields.Many2one('ship.via', 'Ship Via')

#     @api.multi
#     def invoice_validate(self):
#         prefix = ''
#         cr,uid,context = self.env.args
#         if self.partner_id and self.number:
#             country = self.partner_id.country_id.name
#             currency = self.currency_id.name
#             if self.type=='out_invoice':
#                 next_id = self.env['ir.sequence'].get('account.invoice.customer')
#                 self.write({'number': next_id, 'internal_number': next_id})                
#             if self.type=='in_invoice':
#                 next_supp_id = self.env['ir.sequence'].get('account.invoice.supplier')
#                 self.write({'number': next_supp_id, 'internal_number': next_supp_id})                      
#         return self.write({'state': 'open'})

    @api.multi
    def action_date_assign(self):
        for inv in self:
            res = inv.onchange_payment_term_date_invoice(inv.payment_term.id, inv.date_invoice)
            inv_vals = {}
            if res and res.get('value'):
                inv.write(res['value'])
                inv_vals = res['value']
            if inv.journal_id:
                if self.type=='out_invoice':
                    seq_inv = self.env['ir.sequence'].get('account.invoice.customer')
                    inv_vals.update({'number': seq_inv, 'internal_number': seq_inv})
                if self.type=='in_invoice':
                    seq_inv_id = self.env['ir.sequence'].get('account.invoice.supplier')
                    inv_vals.update({'number': seq_inv_id, 'internal_number': seq_inv_id})
            if inv_vals:
                inv.write(inv_vals)
        return True

    @api.multi
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        template = self.env.ref('account.email_template_edi_invoice', False)
        report_template = self.env.ref('stspl_account.stspl_tax_invoice', False)
        if template and report_template:
            template.report_template = report_template.id
            template.report_name = "Tax_Invoice_${(object.number or '').replace('/','_')}_${object.state == 'draft' and 'draft' or ''}"
            template.subject = "${object.company_id.name|safe} Tax Invoice (Ref ${object.number or 'n/a' })"
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.invoice',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


class account_invoice_line(models.Model):
    
    _inherit = 'account.invoice.line'
    
    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='in_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None, context=None):
        cr, uid, context
        res = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom_id, qty, name, type,
                                                      partner_id, fposition_id, price_unit, currency_id=currency_id,
                                                      company_id=company_id, context=context)
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            if partner.show_gst:
                if res and res.get('value', False):
                    res['value'].update({'invoice_line_tax_id': []})
                elif res:
                    res.update({'value': {'invoice_line_tax_id': []}})
        return res


class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    def _prepare_invoice(self,cr,uid,order, line_ids,context=None):
        res = super(purchase_order, self)._prepare_invoice(cr,uid,order, line_ids,context=context)
        res.update({'purchase_id':order.id})
        return  res
    
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
                        report_dict.update({'display_name': 'Quotation','name': 'Quotation',
                                            'string': 'Quotation'})
                    if action_rec.name == 'Purchase Orders' and report_dict.get('report_name',False) and \
                                        report_dict['report_name'] == 'purchase.report_purchasequotation':
                        report_dict.update({'display_name': 'Request for Purchase','name': 'Request for Purchase',
                                            'string': 'Request for Purchase'})
        return result
    
    
class sale_order(models.Model):
    _inherit='sale.order'

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        res=super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context=context)
        res.update({'sales_id':order.id})
        return res

    def action_quotation_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        report_template = ir_model_data.get_object_reference(cr, uid, 'stspl_account', 
                                 'sale_acknowledgment_id')
        if template_id and report_template:
            self.pool.get('email.template').write(cr, uid, [template_id],
                                                  {'report_template': report_template[1]})
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

#    @api.model
#    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#        '''
#        Override this method to Rename Report name to print from Quatation and Sales order menu.
#        '''
#        action_obj = self.env['ir.actions.actions']
#        result = super(sale_order, self).fields_view_get(view_id, 
#            view_type, toolbar=toolbar, submenu=submenu)
#        cr,uid,context = self.env.args
#        if toolbar and context.get('params', False) and context['params'].get('action', False):
#            action_rec = action_obj.browse(context['params']['action'])
#            if result.get('toolbar', False) and result['toolbar'].get('print', False):
#                for report_dict in result['toolbar']['print']:
#                    if action_rec.name == 'Quotations' and report_dict.get('report_name',False) and \
#                                        report_dict['report_name'] == 'stspl_sales.report_sale_order':
#                        report_dict.update({'display_name': 'Quotation','name': 'Quotation',
#                                            'string': 'Quotation'})
#        return result


class account_move(models.Model):
     _inherit = "account.move"

     @api.model
     def create(self, vals):
         if self._context and self._context.get('invoice', False):
             vals['name'] = self._context['invoice'].number or '/'
         return super(account_move, self).create(vals)
     
