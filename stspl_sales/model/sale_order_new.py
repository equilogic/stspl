from datetime import date, datetime
from dateutil import relativedelta
import time

from openerp.osv import fields, osv
from openerp import models,fields,api





class sale_order_new(models.Model):
    _inherit = 'sale.order'

    ship_via_id = fields.Many2one('ship.via.sale', 'Ship Via')



class ship_via_sale(models.Model):
    _name = 'ship.via.sale'
    
    name = fields.Char('Name')