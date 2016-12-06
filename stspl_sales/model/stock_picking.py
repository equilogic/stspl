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
import time

from openerp.osv import fields, osv
from openerp import models,fields,api


class stock_picking_new(models.Model):
    _inherit = 'stock.picking'

    
#    @api.model
#    def create(self,vals):
#        if vals.get('name', '/') == '/':
#            vals['name'] = self.env['ir.sequence'].get('stock.picking.new_seq')
#        res = super(stock_picking_new,self).create(vals)
#        return res
        
