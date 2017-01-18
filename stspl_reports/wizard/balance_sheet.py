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

from openerp.osv import osv  , fields
import tempfile
import xlwt
from xlwt import Workbook
from StringIO import StringIO
import base64
import time
from datetime import datetime, date
from datetime import timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, misc, DEFAULT_SERVER_DATETIME_FORMAT
import time


class wiz_bal_sheet(osv.TransientModel):
    
    _name = 'wiz.bal.sheet'
    
    def _get_fiscalyear(self, cr, uid, context=None):
        return self.pool.get('account.fiscalyear').find(cr, uid, context=context)
    
    def _get_account(self,cr,uid,ids,context=None):
       user_obj = self.pool.get('res.users')
       user_id = user_obj.browse(cr,uid,uid,context=context)
       accounts = self.pool.get('account.account').search(cr,uid,[('parent_id', '=', False), ('company_id', '=', user_id.company_id.id)], context=context,limit=1)
       return accounts and accounts[0] or False
   
    _columns = {
        'chart_account_id' : fields.many2one('account.account', 'Chart of Account', help='Select Charts of Accounts', domain=[('parent_id', '=', False)]),
        'fiscalyear_id' : fields.many2one('account.fiscalyear', "Fiscal Year"),
        'period_to' : fields.many2one('account.period', 'Period To'),
        'company_id' : fields.many2one('res.company', 'Company Id'),
    }
    
    def onchange_chart_account_id(self,cr,uid,ids,chart_account_id = False ,context=None):
        res = {}
        wiz_data = self.read(cr, uid, ids, context=context)[0]
        company_id = wiz_rec.p.company_id
        today_date = datetime.strftime(date.today(), DEFAULT_SERVER_DATE_FORMAT)
        fiscal_year_id = self.pool.get('account.fiscalyear').search(cr,uid,[('company_id', '=', company_id), ('date_start', '<=', today_date), ('date_stop', '>=', today_date)],context=context)
        if fiscal_year_id:
            res['value'] = {'fiscalyear_id': fiscal_year_id[0]}
        return res

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
        res = {}
        if fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period}
        else:
            res['value'] = {'period_from': False, 'period_to': False}
        return res

    
    _defaults = {
        'fiscalyear_id': _get_fiscalyear,
        'chart_account_id':_get_account,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'wiz.general.ledger', context=c),
        }
    
    def check_report(self, cr, uid, ids, context=None):
        
        fl = StringIO()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')

        align_center = xlwt.easyxf('align: horiz center,vert center;font: bold 1, height 300;pattern:pattern solid ,fore_colour aqua;')
        header_1 = xlwt.easyxf('align: horiz center,vert center ;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black;')
        header_2 = xlwt.easyxf('font: bold 1, height 230; align: horiz center,vert center ,wrap 1;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black;pattern:pattern solid ,fore_colour ice_blue;')


        lst = []
        wiz_data = self.read(cr, uid, ids, context=context)[0]
        period_to = wiz_data['period_to'][0]
        chart_account_id = wiz_data['chart_account_id'][0]
        fiscalyear_id = wiz_data['fiscalyear_id'][0]
        fiscalperiod_obj = self.pool.get('account.period')
        finance_obj = self.pool.get('account.financial.report')
        
        period_rec = fiscalperiod_obj.browse(cr, uid, period_to, context)
        company_id = period_rec.company_id.id
        
        periods_ids = fiscalperiod_obj.search(cr, uid, [('date_start', '<=', period_rec.date_start), ('fiscalyear_id', '=', fiscalyear_id), ('company_id', '=', company_id)], context=context)
        
        month_op = datetime.strptime(period_rec.date_start, "%Y-%m-%d")
        date_to = month_op.strftime('%B %d, %Y') 
        date_month = month_op - timedelta (days=1)
        prev_month = datetime.strftime(date_month, "%Y-%m-%d")
        prev_context = {}
        periods_ids_2 = []
        
        if month_op.month == 1:
            get_prev_fiscal = self.pool.get('account.fiscalyear').search(cr, uid, [('date_stop', '=', prev_month), ('company_id', '=', company_id)], context=context)
            if get_prev_fiscal:
                periods_ids_2 = fiscalperiod_obj.search(cr, uid, [('date_start', '<=', prev_month), ('fiscalyear_id', '=', get_prev_fiscal and get_prev_fiscal[0] or False), ('company_id', '=', company_id)], context=context)
        else:
            periods_ids_2 = fiscalperiod_obj.search(cr, uid, [('date_start', '<=', prev_month), ('fiscalyear_id', '=', fiscalyear_id), ('company_id', '=', company_id)], context=context)
        
        if periods_ids_2:
            prev_context.update({'periods':periods_ids_2, 'chart_account_id':chart_account_id, 'company_id':company_id, 'state':'posted'})
        
        date_context = {}
        
        date_stop_str = datetime.strptime(period_rec.date_stop, "%Y-%m-%d")
        current_month_format = datetime.strftime(date_stop_str, "%d-%m-%Y")
        prev_month_format = datetime.strftime(date_month, "%d-%m-%Y")
        
        date_context.update({'current_month':current_month_format, 'prev_month':prev_month_format})
        account_obj = self.pool.get('account.account')

        lines = []


        worksheet.write_merge(1,1,0,0,'',align_center)
        worksheet.write_merge(1,1,1,1,'',align_center)
        worksheet.write_merge(1,1,2,2,'',align_center)
        worksheet.write_merge(1,1,3,3,'',align_center)
        worksheet.write_merge(1,1,4,4,'',align_center)
        company = period_rec.company_id.name
        worksheet.write_merge(1,1,5,5, company,align_center)
        worksheet.write_merge(1,1,6,6,'',align_center)        
        worksheet.write_merge(2,2,0,0,'',align_center)
        worksheet.write_merge(2,2,1,1,'',align_center)
        worksheet.write_merge(2,2,2,2,'',align_center)
        worksheet.write_merge(2,2,3,3,'',align_center)
        worksheet.write_merge(2,2,4,4,'',align_center)
        worksheet.write_merge(2,2,5,5, 'Balance Sheet' + ' ' + date_context['current_month'] + ' ' + 'To' + ' ' + date_context['prev_month'],align_center)              
        worksheet.write_merge(2,2,6,6,'',align_center)
        worksheet.write_merge(3,3,0,0,'',align_center)
        worksheet.write_merge(3,3,1,1,'',align_center)
        worksheet.write_merge(3,3,2,2,'',align_center)
        worksheet.write_merge(3,3,3,3,'',align_center)
        worksheet.write_merge(3,3,4,4,'',align_center)
        worksheet.write_merge(3,3,5,5,'',align_center)
        worksheet.write_merge(3,3,6,6,'',align_center)

        row=4
        col=0
        worksheet.col(0).width = 6000
        worksheet.col(1).width = 1000
        worksheet.col(2).width = 6000
        worksheet.col(3).width = 1000
        worksheet.col(4).width = 6000
        worksheet.col(5).width = 18000
        worksheet.col(6).width = 5000

        blc_lst = []
        bal_sheet_id = self.pool.get("ir.model.data").get_object_reference(cr, uid, "account", "account_financial_report_balancesheet0")[1]
        ids2 = finance_obj._get_children_by_order(cr, uid, [bal_sheet_id], context=context)
        for report in finance_obj.browse(cr, uid, sorted(ids2), context=context):
            vals = {
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type == 'sum' and 'view' or False,
            }
            blc_lst.append(vals)
            print"blc_lst:::::::::::::::::::::::::",blc_lst

        # prev_blc_lst = []
        # for report in finance_obj.browse(cr, uid, sorted(ids2), context=prev_context):
        #     valss = {
        #     'name': report.name,
        #     'prev_balance': report.balance * report.sign or 0.0,
        #     'type': 'report',
        #     'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
        #     'account_type': report.type == 'sum' and 'view' or False,
        #         }
        #     prev_blc_lst.append(valss)
            # print"prev_blc_lst:::::::::::::::::::::::",prev_blc_lst

            # account_ids = []
            # if report.display_detail == 'no_detail':
            #     continue
            # if report.type == 'accounts' and report.account_ids:
            #     account_ids = account_obj._get_children_and_consol(cr, uid, [x.id for x in report.account_ids])
            # elif report.type == 'account_type' and report.account_type_ids:
            #     account_ids = account_obj.search(cr, uid, [('user_type', 'in', [x.id for x in report.account_type_ids]), ('parent_id', 'child_of', chart_account_id)])
            #     # print"account_ids:::::::::::::::::::::",account_ids

            # if account_ids:
            #     for account in account_obj.browse(cr, uid, account_ids, context=context):
            #         if report.display_detail == 'detail_flat' and account.type == 'view':
            #             continue
            #         vals1 = {
            #                 'code':account.code,
            #                 'acc':account,
            #                 'name': account.name,
            #                 'balance':  account.balance != 0 and account.balance * report.sign or account.balance,
            #                 'type': account.type,
            #                 'level':account.level,
            #                 'account_type': account.type,
            #                 'prev_balance':0.0
            #                 }
            #         if prev_context:
            #             if prev_context['periods']:
            #                 prev_account = account_obj.browse(cr, uid, account.id, context=prev_context)
            #                 vals1.update({'prev_balance':  prev_account.balance != 0 and prev_account.balance * report.sign or prev_account.balance})
            #         if vals1['balance'] != 0.0 or vals1['prev_balance'] != 0.0: 
            #             lines.append(vals1)
            #             print"lines::::::::::::::::::::::::::::::",lines
        # row = 6
        # balance = ''
        # previous_balance = ''
        # variance = ''
        # stack_lst = []
        # for data in lines:
        #     balance = ''
        #     previous_balance = ''
        #     variance = ''
        #     if stack_lst:
        #         while stack_lst and stack_lst[-1]['level'] >= data['level']:
        #             ab_name2 = " " * 2 * stack_lst[-1]['level'] + 'Total ' + stack_lst[-1]['name']
        #             balance2 = stack_lst[-1]['balance']
        #             previous_balance2 = stack_lst[-1]['prev_balance']
        #             variance2 = (balance2 - previous_balance2)
        #             worksheet.write(row, 5, ab_name2)
        #             worksheet.write(row, 6, '{0:,.2f}'.format(balance2))
        #             # worksheet.write(row, 2, '{0:,.2f}'.format(previous_balance2))
        #             # worksheet.write(row, 3, '{0:,.2f}'.format(variance2))
        #             row += 1
        #             stack_lst.remove(stack_lst[-1])
        #     if data['type'] == 'view':
        #         stack_lst.append(data)
        #         ab_name = " " * 2 * data['level'] + data['name']
        #         worksheet.write(row, 5, ab_name)
        #         # worksheet.write(row, 1, balance)
        #         # worksheet.write(row, 2, previous_balance)
        #         # worksheet.write(row, 3, variance)
        #         row += 1
        #     else:
        #         worksheet.write(row, 5, " " * 2 * data['level'] + data['name'])
        #         worksheet.write(row, 6, '{0:,.2f}'.format((data.get('balance', 0.0)) ))
        #         # worksheet.write(row, 2, '{0:,.2f}'.format((data.get('prev_balance', 0.0)) ) )
        #         # worksheet.write(row, 3, '{0:,.2f}'.format((data.get('balance', 0.0) - data.get('prev_balance', 0.0))))
        #         row += 1

        # if stack_lst:
        #     stack_lst.reverse()
        #     for acc in stack_lst:
        #         ab_name2 = " " * 2 * acc['level'] + 'Total ' + acc['name']
        #         balance2 = acc['balance']
        #         previous_balance2 = acc['prev_balance']
        #         variance2 = (balance2 - previous_balance2) 

        #         worksheet.write(row, 0, ab_name2)
        #         worksheet.write(row, 1, '{0:,.2f}'.format(balance2))
        #         worksheet.write(row, 2, '{0:,.2f}'.format(previous_balance2))
        #         worksheet.write(row, 3, '{0:,.2f}'.format(variance2))
        #         row += 1
        #     test_row = row
            # col = 0
            # blc = []
            # for liability_data in (blc_lst[-3:]):
            #     blc.append(liability_data.get('balance', 0.0))
                
            #     worksheet.write(row, col, liability_data.get('name', False))
            #     worksheet.write(row, col + 1, '{0:,.2f}'.format(liability_data.get('balance', 0.0)))
            #     row += 1
            # col1 = 2
            
            # for data in (prev_blc_lst[-3:]):
                
            #     worksheet.write(test_row, col1, '{0:,.2f}'.format(liability_data.get('prev_balance', 0.0)))
            #     if blc:
            #         worksheet.write(test_row, col1 + 1, '{0:,.2f}'.format(blc.pop(0) - data.get('prev_balance', 0.0)))
            #     else:
            #         worksheet.write(test_row, col1 + 1,  '{0:,.2f}'.format(0.0 - liability_data.get('prev_balance', 0.0)))
            #     test_row += 1
        workbook.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx = dict(context)
        ctx.update({'file': buf})
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'bal.sheet.excel.export',
                'target': 'new',
                'context': ctx,
                }
        
class bal_sheet_excel_export(osv.TransientModel):
    
    _name = 'bal.sheet.excel.export'
        
    def default_get(self, cr , uid ,fields, context=None):
        if context is None:
            context = {}
            
        res = super(bal_sheet_excel_export, self).default_get(cr,uid,fields,context=context)
        res.update({'name': 'BalanceSheetReport.xls'})
        if context.get('file'):
            res.update({'file': context['file']})
        return res
    
    _columns = {
                
        'file': fields.binary('File'),
        'name' : fields.char(string='File Name', size=32)
    }

    def action_back(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.bal.sheet',
            'target': 'new',
        }

