from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp import models,fields,api


class stock_picking_new(models.Model):
    _inherit = 'stock.picking'

    
    @api.model
    def create(self,vals):
        res = super(stock_picking_new,self).create(vals)
        if res:
            seq_ids = self.env['ir.sequence'].search([('code','=', 'stock.picking.new')])
            if seq_ids:
                next_id = self.env['ir.sequence'].next_by_code('stock.picking.new')
            
                res.write({'name':next_id})
        return res
        
