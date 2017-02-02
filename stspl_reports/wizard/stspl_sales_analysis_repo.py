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


from openerp import models,fields,api
from openerp.exceptions import Warning
from openerp.tools.sql import drop_view_if_exists
from openerp import tools
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from datetime import datetime
import time
#import xlsxwriter
import xlwt
import base64
import random
import math
import tempfile
from xlrd import open_workbook
from StringIO import StringIO
from openerp.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT, ustr


class wiz_sales_analysis_report(models.TransientModel):
	_name = "wiz.sales.analysis.report"


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


	choose_date = fields.Boolean(string="Choose Date For Sales Analysis Xls Report")
	date_start = fields.Date("Start Date", default=lambda *a:time.strftime('%Y-%m-01'))
	date_end = fields.Date("End Date", default = get_end_date)

	@api.multi
	def print_xls_analysis_report(self):
		cr,uid,context=self.env.args
		ctx=dict(context)


		file_path = str('') + '.xlsx'
		workbook = xlsxwriter.Workbook('/tmp/' + file_path)
		worksheet = workbook.add_worksheet()
		worksheet.hide_gridlines(2)


		# Add format
		format_big = workbook.add_format()
		format_big.set_bold()
		format_big.set_font_size(22)
		format_big.set_font_name('Calibri')


		# company_obj = self.env['res.company']
		# for company in company_obj.search([]):
		# 	print"::::::::::::::::::::::::::",company.logo
			

		# 	# url = 'http://python.org/logo.png'
		# 	logo = company.logo
		# 	image_data = StringIO(base64.b64encode (str(logo)))
		# 	print"::::::::::::::::::",image_data
		# 	worksheet.write('B1',image_data)

		worksheet.set_row(8,30)
		worksheet.set_row(33,30)
		worksheet.write('B9', 'ANALYSIS OF SALES FOR FINANCIAL YEAR END' + ' ' + self._get_year() + '( BY MONTH )',format_big)
		worksheet.write('B34', 'ANALYSIS OF SALES FOR FINANCIAL YEAR END' + ' ' + self._get_year() + '( BY PRODUCTS )',format_big)

		
		row = 12
		col = 13

		sale_data = self.env['sale.order'].search([('state', '!=', 'draft'),('date_order', '>=', self.date_start),
					  ('date_order', '<=', self.date_end)])

		if sale_data:

			month = {'Jan': 0.0, 'Feb':0.0, 'Mar':0.0,'Apr':0.0,'May':0.0,'Jun':0.0,'Jul':0.0,'Aug':0.0,'Sep':0.0,'Oct':0.0,'Nov':0.0,'Dec':0.0}
			for data in sale_data:
				if data.date_order:
					converted_date = datetime.strptime(data.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
					date_order_format = datetime.strftime(converted_date, "%b")
					month[date_order_format] = month.get(date_order_format) + data.amount_total
			tot = 0.0
			for i in month.keys():
				if i == 'Jan':
					worksheet.write(row,col,'JAN' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Feb':
					worksheet.write(row,col,'FEB' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Mar':
					worksheet.write(row,col,'MAR' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Apr':
					worksheet.write(row,col,'APR' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'May':
					worksheet.write(row,col,'MAY' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Jun':
					worksheet.write(row,col,'JUN' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Jul':
					worksheet.write(row,col,'JUL' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Aug':
					worksheet.write(row,col,'AUG' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Sep':
					worksheet.write(row,col,'SEP' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Oct':
					worksheet.write(row,col,'OCT' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Nov':
					worksheet.write(row,col,'NOV' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
				if i == 'Dec':
					worksheet.write(row,col,'DEC' + " ' " + self.get_year() or '')
					worksheet.write(row,col + 1, month.get(i) or 0.0)
					tot += month.get(i) or 0.0
					row +=1
			worksheet.write('O25',tot or 0.0)


			# Adding column chart
			column_chart = workbook.add_chart({'type': 'column'})
			column_chart.set_title({'name': 'Sales Analysis Report ( BY MONTH )'})
			column_chart.set_size({'width': 700, 'height': 300})
			column_chart.set_legend({'none': True})
			column_chart_cat = '=Sheet1!$N$13:$N$24'
			column_chart_val = '=Sheet1!$O$13:$O$24'
			column_chart.add_series({
							'categories': column_chart_cat,
							'values': column_chart_val,
							})
			worksheet.insert_chart('B12', column_chart,{'x_offset': 10,'y_offset': 25})

			# Adding pie chart
			pie_chart = workbook.add_chart({'type': 'pie'})
			pie_chart.set_title({'name': ''})
			pie_chart.set_size({'width': 550, 'height': 446})
			pie_chart_cat = '=Sheet1!$N$13:$N$24'
			pie_chart_val = '=Sheet1!$O$13:$O$24'
			pie_chart.add_series({
				'categories': pie_chart_cat,
				'values': pie_chart_val,
				})
			worksheet.insert_chart('B35', pie_chart,{'x_offset': 25,'y_offset': 10})




			workbook.close()
			file = base64.b64encode(open('/tmp/' + file_path, 'read').read())
			ctx.update({'file': file,'name': file_path})
		return {
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				"view_mode": 'form',
				'res_model': 'wiz.stspl.sales.xls.report',
				'target': 'new',
				'context': ctx
			   }


	@api.multi
	def _get_year(self):
		data_data = {}
		if self.date_start:
			date = datetime.strptime(self.date_start,DEFAULT_SERVER_DATE_FORMAT)
			data_data = datetime.strftime(date, "%Y")        
		return data_data

	@api.multi
	def get_year(self):
		data_data = {}
		if self.date_start:
			date = datetime.strptime(self.date_start,DEFAULT_SERVER_DATE_FORMAT)
			data_data = datetime.strftime(date, "%y")        
		return data_data

	
class wiz_stspl_sales_xls_report(models.TransientModel):
	_name = "wiz.stspl.sales.xls.report"

	file = fields.Binary('File')
	name = fields.Char(string='File Name', size=64)

	@api.model
	def default_get(self, fields):
		super(wiz_stspl_sales_xls_report, self).default_get(fields)
		cr, uid, context = self.env.args
		res = dict(context)
		vals = {'name': 'Stspl Sales Report.xls'}
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
			'res_model': 'wiz.sales.analysis.report',
			'target': 'new',
		}



class sales_report(models.Model):
	_name = "stspl.sales.report"

	date = fields.Datetime('Date Order', readonly=True)
	product_id = fields.Many2one('product.product', 'Product', readonly=True)
	product_uom = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)
	product_uom_qty = fields.Float('# of Qty', readonly=True)
	price_total = fields.Float('Total Price', readonly=True)
	state = fields.Selection([
						('cancel', 'Cancelled'),
						('draft', 'Draft'),
						('confirmed', 'Confirmed'),
						('exception', 'Exception'),
						('done', 'Done')], 'Order Status', readonly=True)
	pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)

	_auto = False

	def _select(self):
		select_str = """
			WITH currency_rate (currency_id, rate, date_start, date_end) AS (
					SELECT r.currency_id, r.rate, r.name AS date_start,
						(SELECT name FROM res_currency_rate r2
						WHERE r2.name > r.name AND
							r2.currency_id = r.currency_id
						 ORDER BY r2.name ASC
						 LIMIT 1) AS date_end
					FROM res_currency_rate r
				)
			 SELECT min(l.id) as id,
					l.product_id as product_id,
					t.uom_id as product_uom,
					sum(l.product_uom_qty * l.price_unit / cr.rate * (100.0-l.discount) / 100.0) as price_total,
					s.date_order as date,
					l.state,
					s.pricelist_id as pricelist_id
		"""
		return select_str

	def _from(self):
		from_str = """
				sale_order_line l
					  join sale_order s on (l.order_id=s.id)
						left join product_product p on (l.product_id=p.id)
							left join product_template t on (p.product_tmpl_id=t.id)
					left join product_uom u on (u.id=l.product_uom)
					left join product_uom u2 on (u2.id=t.uom_id)
					left join product_pricelist pp on (s.pricelist_id = pp.id)
					join currency_rate cr on (cr.currency_id = pp.currency_id and
						cr.date_start <= coalesce(s.date_order, now()) and
						(cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
		"""
		return from_str

	def _group_by(self):
		group_by_str = """
			GROUP BY l.product_id,
					l.order_id,
					t.uom_id,
					s.date_order,
					l.state,
					s.pricelist_id
		 
		"""
		return group_by_str

	def init(self, cr):
		tools.drop_view_if_exists(cr, self._table)
		cr.execute("""CREATE or REPLACE VIEW %s as (
			%s
			FROM ( %s )
			%s
			)""" % (self._table, self._select(), self._from(), self._group_by()))
