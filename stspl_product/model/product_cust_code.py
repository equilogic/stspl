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
from openerp import api,fields,models


class product_cust_code(models.Model):
    
    _name = "product.cust.code"
    _description = "Add many Code of Customer's"
    
    _rec_name = 'prod_code'
    
    prod_code = fields.Char('Customer Product Code',help="""This customer's product code
                                            will be used when searching into
                                            a request for quotation.""")
    prod_name = fields.Char('Customer Product Name',help="""This customer's product code
                                            will be used when searching into
                                            a request for quotation.""")
    prod_id = fields.Many2one('product.product', 'Product')

    partner_id = fields.Many2one('res.partner', 'Customer')
    company_id = fields.Many2one('res.company',string='Company',
                                 defaults=lambda s, c: s.pool.get('res.company').
        _company_default_get(cr, uid,'product.cust.code'))

    _sql_constraints = [
        ('unique_code', 'unique(prod_code,company_id,partner_id)',
         'Product Code of customer must be unique'),
    ]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

