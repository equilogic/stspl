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



from openerp import fields,models,api
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
import time
from openerp import tools
import xlwt
import base64
import tempfile
from xlrd import open_workbook
from StringIO import StringIO
from datetime import datetime
from openerp.tools import misc, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.sql import drop_view_if_exists


class stock_history(models.TransientModel):
	_inherit = 'wizard.valuation.history'

	@api.model
	def get_end_date(self):
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

	date_choose = fields.Boolean(string="Choose Date For Xls Product Valuation")
	date_start = fields.Date(string="Start Date",default=lambda *a:time.strftime('%Y-%m-01'),required=True)
	date_end = fields.Date(string="End Date",default = get_end_date,required=True)

	@api.multi
	def xls_show_product(self):
		cr,uid,context = self.env.args
		
		fl = StringIO()
		cr,uid,context=self.env.args
		ctx=dict(context)

		   
		workbook = xlwt.Workbook(encoding='utf-8')
		worksheet = workbook.add_sheet('New Sheet')


		align_center = xlwt.easyxf('align: horiz center,vert center;font: bold 1, height 300;pattern:pattern solid ,fore_colour aqua;')
		header_1 = xlwt.easyxf('align: horiz center,vert center ;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black;')
		header_2 = xlwt.easyxf('font: bold 1, height 230; align: horiz center,vert center ,wrap 1;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black;pattern:pattern solid ,fore_colour ice_blue;')

		worksheet.write_merge(0,0,0,4,'',align_center)
		worksheet.write_merge(1,1,0,4, 'STSPL' + ' ' + self._get_year(),align_center)
		worksheet.write_merge(2,2,0,4, 'Stock Valuation' + ' ' + self._get_start_date() + ' ' + 'To' + ' ' + self._get_end_date(),align_center)
		worksheet.write_merge(3,3,0,4,'',align_center)

		row=5
		col=0
		worksheet.row(1).height=400
		worksheet.row(row).height=550
		worksheet.col(0).width = 5000
		worksheet.col(1).width = 11000
		worksheet.col(2).width = 4000
		worksheet.col(3).width = 4000
		worksheet.col(4).width = 4000

		
		worksheet.write(row, col, "CODE",header_2)
		col+=1
		worksheet.write(row, col, "PRODUCT",header_2)
		col+=1
		worksheet.write(row, col, "QUANTITY",header_2)
		col+=1
		worksheet.write(row, col, "UNIT PRICE",header_2)
		col+=1
		worksheet.write(row, col, "VALUE",header_2)
		col+=1
		row+=1


		product_obj = self.env['product.product']

		product_data = product_obj.search([('create_date', '>=', self.date_start),('create_date', '<=', self.date_end)])

		for product in product_data:

			worksheet.row(row).height=400
			col=0
			worksheet.write(row, col, product['default_code'] or '',header_1)
			col+=1
			worksheet.write(row, col, product['name'] or '',header_1)
			col+=1
			worksheet.write(row, col, product['qty_available'] or '',header_1)
			col+=1
			worksheet.write(row, col, product['standard_price'] or '',header_1)
			col+=1
			worksheet.write(row, col, product['list_price'] or '',header_1)
			col+=1
			row+=1

		workbook.save(fl)
		fl.seek(0)
		buf = base64.encodestring(fl.read())
		ctx.update({'file':buf})
		return{
			'type':'ir.actions.act_window',
			'view_type':'form',
			'view_mode':'form',
			'res_model':'wiz.stspl.product.valuation.xls.report',
			'target':'new',
			'context':ctx
		}


	@api.multi
	def _get_year(self):
		data_data = {}
		if self.date_start:
			date = datetime.strptime(self.date_start,DEFAULT_SERVER_DATE_FORMAT)
			data_data = datetime.strftime(date, "%Y")        
		return data_data


	@api.multi
	def _get_start_date(self):
		data_data = {}
		if self.date_start:
			date = datetime.strptime(self.date_start,DEFAULT_SERVER_DATE_FORMAT)
			data_data = datetime.strftime(date, "%d-%m-%Y")        
		return data_data


	@api.multi
	def _get_end_date(self):
		data_data = {}
		if self.date_start:
			date = datetime.strptime(self.date_end,DEFAULT_SERVER_DATE_FORMAT)
			data_data = datetime.strftime(date, "%d-%m-%Y")        
		return data_data


class wiz_stspl_product_valuation_xls_report(models.TransientModel):
	_name = "wiz.stspl.product.valuation.xls.report"

	file = fields.Binary('File')
	name = fields.Char(string='File Name', size=64)

	@api.model
	def default_get(self, fields):
		super(wiz_stspl_product_valuation_xls_report, self).default_get(fields)
		cr, uid, context = self.env.args
		res = dict(context)
		vals = {'name': 'Stspl Product Valuation Report.xls'}
		if context.get('report_name', False):
			vals = {'name': context['report_name']}
		res.update(vals)
		self.env.args = cr, uid, misc.frozendict(res)
		if context.get('file'):
			vals1 = {'file': context['file']}
			cr, uid, context = self.env.args
			res = dict(context)
			res.update(vals1)
			self.env.args = cr, uid, misc.frozendict(res)
		return res

	@api.multi
	def back(self):
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'wizard.valuation.history',
			'target': 'new'
		}