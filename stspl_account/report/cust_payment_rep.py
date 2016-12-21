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

class report_print_cust_payment_rep(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_print_cust_payment_rep, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_inv_details': self._get_inv_details
        })

    def _get_inv_details(self, voucher):
        v_line_lst = []
        if voucher:
            voucher_ids = self.pool.get('account.voucher.line').search(self.cr, self.uid, [('voucher_id','=',voucher.id)])
            if voucher_ids:
                for v_line in self.pool.get('account.voucher.line').browse(self.cr, self.uid, voucher_ids):
                    if v_line.move_line_id and v_line.move_line_id.invoice:
                        v_line_lst.append(v_line.id)
        if v_line_lst:
            v_line_lst = list(set(v_line_lst))
            v_line_lst = self.pool.get('account.voucher.line').browse(self.cr, self.uid, v_line_lst)
        return v_line_lst

class report_print_cust_payment_rep_extended(models.AbstractModel):
    _name = 'report.stspl_account.report_stspl_customer_payment'
    _inherit = 'report.abstract_report'
    _template = 'stspl_account.report_stspl_customer_payment'
    _wrapped_report_class = report_print_cust_payment_rep

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: