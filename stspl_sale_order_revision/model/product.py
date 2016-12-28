# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services Pvt. Ltd. (<http://serpentcs.com>).
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

from openerp import fields, models, api
from openerp.tools.translate import _


class product_template(models.Model):
    _inherit = "product.template"

    markup_amt = fields.Float(string="Markup Amount")
    shipment_amt = fields.Float(string="Shipment Amount")
    operation_amt = fields.Float(string="Operation Amount")
    expense_amt = fields.Float(string="Expense Amount")
    pure_profit_amt = fields.Float(string="Pure Profit Amount")
    prod_alias_name = fields.Char(string="Product Alias First")
    prod_alias_name1 = fields.Char(string="Product Alias Second")
    
    