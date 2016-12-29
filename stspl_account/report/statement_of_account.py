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


import time
from openerp.report import report_sxw
from openerp import models
import time
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import except_orm
from dateutil.relativedelta import relativedelta


class report_statement_of_account(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(report_statement_of_account, self).__init__(cr, uid, name, context=context)
        self.start_date = ''
        self.total_account = []
        self.total = 0.0
        self.all_inv_total = 0.0
        self.localcontext.update({
            'time': time,
            'get_start_partners': self.get_start_partners,
            'get_date': self.get_date,
            'lines': self.lines,
            'date_part': self.date_part,
            'get_move_data':self.get_move_data,
            'get_all_total':self.get_all_total
        })



    def get_date(self, form):
        data_data = {}
        if form.get('start_date', False):
            date = datetime.strptime(str(form.get('start_date', False)), "%Y-%m-%d")
            data_data.update({'month': date.strftime("%b") + ' ' + date.strftime("%Y"),
                              'date': form.get('start_date', False)})
        self.start_date = form.get('start_date', False)
        date_today = datetime.today()
        data_data.update({'date': date_today})        
        return data_data
    

    def get_start_partners(self, form):
        partner_obj = self.pool.get('res.partner')
        lst = []
        result={}
        attn_dict={}
        data = []
        self.start_date = form.get('start_date', False)
        data2 = []
        if form.get('customer_ids', False):
            partners = partner_obj.browse(self.cr, self.uid, form.get('customer_ids', []))
            for partner in partners:
                date_data = self.date_part(partner)
                for key, value in date_data[0].items():
                    data2 = self.get_move_data(value['start'], value['stop'], partner)
                    if data2:
                        if partner not in lst:
                            lst.append(partner)
                            attn_id = partner_obj.search(self.cr, self.uid,[('parent_id','=',partner.id),('type','=','other')])
                            attn = partner_obj.browse(self.cr, self.uid, attn_id).name
                            attn_dict.update({partner:attn})
            result.update({'list':lst,'attn':attn_dict})
        return result
    
    def lines(self, partner):
        inv_list = []
        total = 0.0
        inv_id_list = []
        
        if partner:
            inv_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('partner_id', '=', partner.id),
                                                                     ('state', 'not in', ('draft', 'cancel', 'paid')),
                                                                     ('type', 'in', ('out_invoice', 'out_refund')),
                                                                     ('date_invoice', '<=', self.start_date),
                                                                     ], order = 'date_invoice desc')                         
            if inv_ids:
                for inv_data in self.pool.get('account.invoice').browse(self.cr, self.uid, inv_ids):
                    inv_dict = {}
                    date_invoice_format = ''
                    date_due_format = ''
                    if inv_data.type == 'out_invoice':
                        total += inv_data.residual
                        inv_dict.update({'debit': inv_data.residual and inv_data.residual or 0.0})
                        inv_dict.update({'credit': 0.0})
                        if inv_data.payment_ids:
                            debit = 0.0
                            credit = 0.0
                            for payment_rec in inv_data.payment_ids:
                                if inv_data.company_id.currency_id.id != inv_data.currency_id.id:
                                    credit += abs(payment_rec.amount_currency)
                                else:
                                    credit += payment_rec.credit
                                inv_dict.update({'credit':credit or 0.0})
                                inv_dict.update({'debit': inv_data.residual and inv_data.residual or 0.0})
                    if inv_data.type == 'out_refund':
                        total -= inv_data.residual
                        debit = 0.0
                        inv_dict.update({'credit': inv_data.residual and inv_data.residual or 0.0})
                        for payment_rec in inv_data.payment_ids:
                                if inv_data.company_id.currency_id.id != inv_data.currency_id.id:
                                    debit -= abs(payment_rec.amount_currency)
                                else:
                                    debit += payment_rec.credit                            
                                inv_dict.update({'debit': debit or 0.0})
                    if inv_data.date_invoice:
                        converted_date = datetime.strptime(inv_data.date_invoice, DEFAULT_SERVER_DATE_FORMAT)
                        date_invoice_format = datetime.strftime(converted_date, "%d-%m-%Y")

                    if inv_data.date_due:
                        converted_date = datetime.strptime(inv_data.date_due, DEFAULT_SERVER_DATE_FORMAT)
                        date_due_format = datetime.strftime(converted_date, "%d-%m-%Y")

                    inv_dict.update({
                                     'date': date_invoice_format,
                                     'inv_no': inv_data.number,
                                     'due_date':date_due_format,
                                     'total': total})
                    inv_list.append(inv_dict)

        self.all_inv_total = total
        print":::::::::::::::::::::::::;inv_list",inv_list
        return inv_list


    def get_all_total(self):
        return self.all_inv_total
    

    def date_part(self, partner):
        res = {}
        date_data = []
        start = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
        for i in range(4)[::-1]:
            stop = start - relativedelta(days=30)
            try:
                res[str(i)] = {
                    'name': (i != 0 and (str((4 - (i + 1)) * 30) + '-' + str((4 - i) * 30)) or ('' + str(3 * 30))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
                }
            except Exception as ex:
                raise except_orm(_('User Error'), _('Please select Valid date'))
            start = stop - relativedelta(days=1)
        date_data.append(res)
        return date_data

    
    def get_move_data(self, date_s, date_e, partner):
        inv_ids = []
        if partner and date_s and date_e:
            inv_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('partner_id', '=', partner.id),
                                                                         ('state', 'not in', ('draft', 'cancel', 'paid')),
                                                                         ('type', 'in', ('out_invoice', 'out_refund')),
                                                                         ('date_due', '<=', date_e),
                                                                         ('date_due', '>=', date_s), ])
        if partner and not date_s:
            if inv_ids:
                inv_ids.append(self.pool.get('account.invoice').search(self.cr, self.uid, [('partner_id', '=', partner.id),
                                                                         ('state', 'not in', ('draft', 'cancel', 'paid')),
                                                                         ('type', '=', 'out_invoice'),
                                                                         ('date_due', '<=', date_e),
                                                                         ],)) 
            else:
                inv_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('partner_id', '=', partner.id),
                                                                         ('state', 'not in', ('draft', 'cancel', 'paid')),
                                                                         ('type', 'in', ('out_invoice', 'out_refund')),
                                                                         ('date_due', '<=', date_s),
                                                                         ],)               
        amt = 0.0
        if inv_ids:
            for inv_data in self.pool.get('account.invoice').browse(self.cr, self.uid, inv_ids):
                if inv_data.type =='out_invoice':
                    amt += inv_data.residual
                if inv_data.type =='out_refund':
                    amt -= inv_data.residual
        return amt 


class report_print_sales_statement_of_account_extended(models.AbstractModel):
    _name = 'report.stspl_account.stspl_account_statement_of_account_template'
    _inherit = 'report.abstract_report'
    _template = 'stspl_account.stspl_account_statement_of_account_template'
    _wrapped_report_class = report_statement_of_account
