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


