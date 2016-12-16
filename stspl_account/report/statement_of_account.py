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

import time
from openerp.report import report_sxw
from openerp import models
import time
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import except_orm
from dateutil.relativedelta import relativedelta

class report_statement_of_account(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_statement_of_account, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_company':self._get_company,
            'get_customer':self._get_customer,
            'lines':self.lines
        })


    def _get_company(self,data):
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        return user and user.company_id or False


    def _get_customer(self, form):
            result = []
            emp = self.pool.get('res.partner')
            result = emp.browse(self.cr, self.uid, form['customer_ids'])
            return result



    def lines(self,data):

        inv_list = []

        if data:
            inv_ids = self.pool.get('account.invoice').search(self.cr, self.uid, \
                                                    [('partner_id', 'in', data['form']['customer_ids'])])
            print "\n inv_ids :::::::::", inv_ids
            if inv_ids:
                inv_list = self.pool.get('account.invoice').browse(self.cr, self.uid, inv_ids)
                print "inv_list:::::::::::::::::::::::::",inv_list

        return inv_list




#     def lines(self, partner):
#         inv_list = []
#         total = 0.0
#         inv_id_list = []
#         if partner:
#             inv_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('partner_id', '=', partner.id),
#                                                                      ('state', 'not in', ('draft', 'cancel', 'paid')),
#                                                                      ('type', 'in', ('out_invoice', 'out_refund')),
#                                                                      ('date_invoice', '<=', self.start_date),
#                                                                      # ('freight_other_charges', '=', False),
#                                                                      ], order = 'date_invoice desc')
#             if inv_ids:
#                 for inv in inv_ids:
#                     inv_id_list.append(inv) 
                            
#             if inv_id_list:
#                 for inv_data in self.pool.get('account.invoice').browse(self.cr, self.uid, inv_id_list):
#                     inv_dict = {}
#                     if inv_data.type == 'out_invoice':
#                         total += inv_data.residual
#                         inv_dict.update({'debit': inv_data.residual and inv_data.residual or 0.0})
#                         inv_dict.update({'credit': 0.0})
#                         if inv_data.payment_ids:
#                             debit = 0.0
#                             credit = 0.0
#                             for payment_rec in inv_data.payment_ids:
#                                 if inv_data.company_id.currency_id.id != inv_data.currency_id.id:
#                                     credit += abs(payment_rec.amount_currency)
#                                 else:
#                                     credit += payment_rec.credit
#                                 inv_dict.update({'credit':credit or 0.0})
#                                 inv_dict.update({'debit': inv_data.residual and inv_data.residual or 0.0})
#                     if inv_data.type == 'out_refund':
#                         total -= inv_data.residual
#                         debit = 0.0
#                         inv_dict.update({'credit': inv_data.residual and inv_data.residual or 0.0})
#                         for payment_rec in inv_data.payment_ids:
#                                 if inv_data.company_id.currency_id.id != inv_data.currency_id.id:
#                                     debit -= abs(payment_rec.amount_currency)
#                                 else:
#                                     debit += payment_rec.credit                            
# #                                 debit += payment_rec.debit
#                                 inv_dict.update({'debit': debit or 0.0})
#                     inv_dict.update({
#                                      'date': inv_data.date_invoice,
#                                      'ref': inv_data.number,
#                                      'desc': inv_data.comment,
#                                      'total': total})

#                     inv_list.append(inv_dict)
#         self.all_inv_total = total
# #         newlist = sorted(inv_list, key=lambda k: k['date'], reverse=True)
#         return inv_list


    # def lines(self,data):

    #     soa_data = []

    #     if data:
    #         invoices = self.pool.get('account.invoice').search(self.cr, self.uid,[('partner_id','=',data.id),('type','=','out_invoice')])
    #         print "invoices::::::::::::::::::::::::::::::::::", invoices
    #         if invoices:
    #             invoices = self.pool.get('account.invoice').browse(self.cr, self.uid, invoices)
    #     return invoices




class report_print_sales_statement_of_account_extended(models.AbstractModel):
    _name = 'report.stspl_account.stspl_account_statement_of_account_template'
    _inherit = 'report.abstract_report'
    _template = 'stspl_account.stspl_account_statement_of_account_template'
    _wrapped_report_class = report_statement_of_account