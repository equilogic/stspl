# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


from openerp.report import report_sxw
from openerp import models, api, _, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class report_print_sale_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_print_sale_order, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_qty':self._get_qty,
            'get_etd':self._get_etd,
            
        })

    def _get_qty(self, qty):
        return int(qty)
    
    def _get_etd(self, picking_ids,product_id):
        for pick in picking_ids:
            for line in pick.move_lines:
                if product_id.id == line.product_id.id:
                    converted_date = datetime.strptime(line.date_expected, '%Y-%m-%d %H:%M:%S')
                    date_formatted = datetime.strftime(converted_date, "%d-%m-%Y")
                    return date_formatted
        return ''


        
        
    
class report_print_sale_order_extended(models.AbstractModel):
    _name = 'report.stspl_sales.report_sale_order'
    _inherit = 'report.abstract_report'
    _template = 'stspl_sales.report_sale_order'
    _wrapped_report_class = report_print_sale_order
