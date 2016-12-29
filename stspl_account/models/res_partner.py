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

from openerp import models, fields, api, _



class res_partner(models.Model):
    
    _inherit = 'res.partner'

    show_gst = fields.Boolean(string="Show GST")
    grn_number = fields.Char('GRN No.')
    
    @api.multi
    @api.constrains('grn_number', 'supplier', 'customer')
    def _check_grn_number(self):
        for partner in self:
            if partner.grn_number and partner.customer:
                customers = self.env['res.partner'].search([('customer', '=', True),
                                                ('grn_number', '=', partner.grn_number)])
                if customers and len(customers.ids) > 1:
                    raise Warning(_('GRN Number must be unique for customer !'))
            if partner.grn_number and partner.supplier:
                suppliers = self.env['res.partner'].search([('supplier', '=', True),
                                                ('grn_number', '=', partner.grn_number)])
                if suppliers and len(suppliers.ids) > 1:
                    raise Warning(_('GRN Number must be unique for supplier !'))

#     _sql_constraints = [('grn_unique', 'unique(grn_number)',
#                          'GRN Number must be unique!')]
