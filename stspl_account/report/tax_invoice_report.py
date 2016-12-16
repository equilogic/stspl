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


from openerp.report import report_sxw
from openerp import models, api, _, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class report_print_tax_invoice_stspl(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_print_tax_invoice_stspl, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_qty':self._get_qty,
            'get_sal_do_num':self._get_sal_do_num,
            'get_sgd_details': self._get_sgd_details,
            'get_lines_if_discount': self._get_lines_if_discount
        })

    def _get_qty(self, qty):
        return int(qty)
    
    def _get_lines_if_discount(self, inv_lines):
        flag = False
        if inv_lines:
            for line in inv_lines:
                if line.discount and line.discount > 0.0:
                    flag = True
        return flag

    def _get_sgd_details(self, inv, inv_currency):
        curr_sgd = self.pool.get('res.currency').search(self.cr, self.uid, [('name', '=', 'SGD')])
        sgd_result = [{'rate':0.0, 'before_gst':0.0, 'gst_amt': 0.0, 'after_amt': 0.0}]
        if curr_sgd:
            curr_sgd_rec = self.pool.get('res.currency').browse(self.cr, self.uid, curr_sgd[0])
            sgd_result[0].update({'rate': curr_sgd_rec.rate_silent or 0.0})
            if inv_currency and inv and inv.amount_untaxed:
                exchange_rate = curr_sgd_rec.rate_silent / inv_currency.rate_silent
                sgd_result[0].update({'before_gst': inv.amount_untaxed * exchange_rate})
            if inv_currency and inv and inv.amount_tax:
                exchange_rate = curr_sgd_rec.rate_silent / inv_currency.rate_silent
                sgd_result[0].update({'gst_amt': inv.amount_tax * exchange_rate})
            if inv_currency and inv and inv.amount_total:
                exchange_rate = curr_sgd_rec.rate_silent / inv_currency.rate_silent
                sgd_result[0].update({'after_amt': inv.amount_total * exchange_rate})
        return sgd_result
    
    def _get_sal_do_num(self,picking_ids):
        if picking_ids:
            for pick in picking_ids:
                if pick.picking_type_id.name == 'Delivery Orders':
                    return pick.name
        return ''

class report_print_tax_invoice_stspl_extended(models.AbstractModel):
    _name = 'report.stspl_account.report_stspl_tax_invoice'
    _inherit = 'report.abstract_report'
    _template = 'stspl_account.report_stspl_tax_invoice'
    _wrapped_report_class = report_print_tax_invoice_stspl




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: