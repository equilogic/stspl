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


