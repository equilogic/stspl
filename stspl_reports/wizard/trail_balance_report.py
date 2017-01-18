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

from openerp.osv import osv,fields
from datetime import date, timedelta, datetime, tzinfo
import tempfile
import xlwt
from xlwt import Workbook
from StringIO import StringIO
import base64
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, misc, DEFAULT_SERVER_DATETIME_FORMAT


class wiz_trial_balance(osv.TransientModel):
    
    _name = 'wiz.trial.balance'
   
    def _get_start_date(self, cr, uid, ids, context=None):
        fiscal_year_obj = self.pool.get('account.fiscalyear')
        fiscalyear_id = fiscal_year_obj.find(cr, uid, context=context)
        date = fiscal_year_obj.browse(cr, uid, fiscalyear_id, context=context).date_start
        return date


    def _get_end_date(self, cr, uid, ids, context=None):
        today = datetime.now().date()
        last_days = [31, 30, 29, 28, 27]
        for i in last_days:
            try:
                end = datetime(today.year, today.month, i)
            except ValueError:
                continue
            else:
                return end.date()
        return None
   
    def _get_account(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user_id = user_obj.browse(cr, uid, uid, context=context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user_id.company_id.id)], limit=1)
        return accounts and accounts[0] or False
    
    _columns = {
        'chart_account_id' : fields.many2one('account.account', 'Chart of Account', help='Select Charts of Accounts', domain=[('parent_id', '=', False)]),
        'start_date' : fields.date('Start Date'),
        'end_date' : fields.date('End Date'),
    }
    _defaults = {
        'start_date': _get_start_date,
        'end_date':_get_end_date,
        'chart_account_id':_get_account,
        }
     
    def xls_trail_balance(self, cr, uid, ids, context=None):
        wiz_rec = self.browse(cr,uid,ids,context=context)[0]
        fis_comp = wiz_rec.chart_account_id.company_id.name
        date_obj = self.pool.get('account.period')
        start_date = date_obj.browse(cr,uid,uid,context=context)
        start_dt = start_date.date_start
        dt_end = wiz_rec.end_date
        vals = {}
        vals['start_date'] = start_dt
        vals['end_date'] = dt_end
        vals['company_id'] = wiz_rec.chart_account_id.company_id.id
        vals['chart_account_id'] = wiz_rec.chart_account_id.id
        vals['state'] = 'posted'
        context = dict(context)
        context.update(vals)
        account_ids = self.pool.get('account.account').search(cr,uid,[('type', '!=', 'view'), ('company_id', '=', wiz_rec.chart_account_id.company_id.id)])
        accounts = self.pool.get('account.account').browse(cr,uid,account_ids,context=context)

        date = datetime.strptime(wiz_rec.start_date,DEFAULT_SERVER_DATE_FORMAT)
        start_date = datetime.strftime(date, "%d-%m-%Y") 

        date = datetime.strptime(wiz_rec.end_date,DEFAULT_SERVER_DATE_FORMAT)
        end_date = datetime.strftime(date, "%d-%m-%Y")        

        
        fl = StringIO()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')

        align_center = xlwt.easyxf('align: horiz center,vert center;font: bold 1, height 300;pattern:pattern solid ,fore_colour aqua;')
        header = xlwt.easyxf('font: bold 1, height 230; align: horiz center,vert center ,wrap 1;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black;pattern:pattern solid ,fore_colour ice_blue;')

        worksheet.write_merge(0,0,0,2,'',align_center)
        worksheet.write_merge(1,1,0,2,fis_comp,align_center)
        worksheet.write_merge(2,2,0,2,'Trail Balance' + ' ' + start_date + ' ' + 'To' + ' ' + end_date,align_center)
        worksheet.write_merge(3,3,0,2,'',align_center)

        row=5
        col=0
        worksheet.row(1).height=400
        worksheet.row(row).height=550
        worksheet.col(0).width = 11000
        worksheet.col(1).width = 5500
        worksheet.col(2).width = 5500

        
        worksheet.write(row, col, "Account",header)
        col+=1
        worksheet.write(row, col, "Debit",header)
        col+=1
        worksheet.write(row, col, "Credit",header)
        col+=1
        row+=1


        total_credit = 0.0
        total_debit = 0.0
        A=6
        for account in accounts:
            if account.debit != 0 or account.credit != 0:
                total_credit += account.credit
                total_debit += account.debit
                
                worksheet.write(A, 0, account.name)
                worksheet.write(A, 1, '{0:,.1f}'.format(account.debit))
                worksheet.write(A, 2, '{0:,.1f}'.format(account.credit))
                A+=1
                
        worksheet.write(A + 1, 0, 'TOTAL')
        worksheet.write(A + 1, 1, '{0:,.1f}'.format(total_debit))
        worksheet.write(A + 1, 2, '{0:,.1f}'.format(total_credit))

        
        workbook.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx = dict(context)
        ctx.update({'file': buf})
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.trial.balance.standard.export',
                'target': 'new',
                'context': ctx,
        }
        
        
class account_trial_balance_standard_export(osv.TransientModel):
    
    _name = 'account.trial.balance.standard.export'
        
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
            
        res = super(account_trial_balance_standard_export, self).default_get(cr, uid, fields, context=context)
        res.update({'name': 'Stspl Trial Balance.xls'})
        if context.get('file'):
            res.update({'file': context['file']})
        return res
    _columns = {
        'file' : fields.binary('File'),
        'name' : fields.char(string='File Name', size=32),
    }
    def action_back(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.trial.balance',
            'target': 'new',
        }
        


