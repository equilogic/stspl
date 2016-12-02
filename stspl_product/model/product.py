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
#from openerp.osv import osv, fields


class product_product(models.Model):
    _inherit = 'product.product'
    
    prod_cust_code_ids = fields.One2many('product.cust.code',
                                                     'prod_id',
                                                     'Customer Codes')
#    prod_cust_ids = fields.One2many('product.cust.code','product_id',string='Customer Codes')
                                                     

    @api.one
    def copy(self, default=None):
        if not default:
            default = {}
        default['prod_cust_code_ids'] = False
        res = super(product_product, self).copy(default=default)
        return res
    
    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=80):
        
        res = super(product_product, self).name_search(
            cr, user, name, args, operator, context, limit)

        if not context:
            context = {}

        product_customer_code_obj = self.pool.get('product.cust.code')
        if not res:
            ids = []
            arg=[('prod_code','=', name),('partner_id', '=',partner_id)]
            partner_id = self._context.get('partner_id', False)
            
            
            if partner_id:
                id_prod_code = \
                    product_customer_code_obj.search(cr,user,arg,limit=limit,context=context)
                # TODO: Search for product customer name
                id_prod = id_prod_code and product_customer_code_obj.browse(
                    cr, user, id_prod_code, context=context) or []
                for ppu in id_prod:
                    ids.append(ppu.prod_id.id)
            if ids:
                res = self.name_get(cr, user, ids, context)
        return res
class product_template(models.Model):
    _inherit = 'product.template'

    remark = fields.Char('Remarks')
    brand = fields.Many2one('brand.brand', string="Brand")
    code = fields.Char(string="Code")
    hs_code = fields.Char(string="HS Code")
class brand(models.Model):
    _name = 'brand.brand'
    _description = "Product Brand"

    name = fields.Char('Name')
    code = fields.Char('Code')


class ship_via(models.Model):
    _name = 'ship.via'
    
    name = fields.Char('Name')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
