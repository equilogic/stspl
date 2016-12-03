from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp import models,fields,api


class account_invoice(models.Model):
    
    _inherit = 'account.invoice'

    purchase_id= fields.Many2one('purchase.order','Prchase Id')
    sales_id=fields.Many2one('sale.order','Sales Id')

    @api.model
    def create(self,vals):
        res = super(account_invoice,self).create(vals)
        if res:
            seq_ids = self.env['ir.sequence'].search([('code','=', 'account.invoice.new')])
            if seq_ids:
                next_id = self.env['ir.sequence'].next_by_code('account.invoice.new')
            
                res.write({'number':next_id})
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        '''
        Override this method to remove reports from Supplier invoice menu.
        '''
        action_obj = self.env['ir.actions.actions']
        result = super(account_invoice, self).fields_view_get(view_id, 
            view_type, toolbar=toolbar, submenu=submenu)
        cr,uid,context = self.env.args
        if toolbar and context.get('params', False) and context['params'].get('action', False):
            action_rec = action_obj.browse(context['params']['action'])
            if result.get('toolbar', False) and result['toolbar'].get('print', False):
                dict_lst = []
                for report_dict in result['toolbar']['print']:
                    if action_rec.name == 'Supplier Invoices' and report_dict.get('report_name',False):
                        if report_dict['report_name'] in ['stspl_account.report_packing_list','stspl_account.report_sale_acknowledgment']:
                            dict_lst.append(report_dict)
                if action_rec.name == 'Supplier Invoices' and report_dict.get('report_name',False) and dict_lst:
                    for dict in dict_lst:
                        report_index = result['toolbar']['print'].index(dict)
                        result['toolbar']['print'].pop(report_index)
        return result


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    ship_via_id = fields.Many2one('ship.via.purchase', 'Ship Via')
    
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


