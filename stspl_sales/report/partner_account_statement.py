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


class report_partner_account_statement(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(report_partner_account_statement, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
			'get_company':self._get_company,
			'get_warehouse':self._get_warehouse,
			'get_attns': self._get_attns
		})


	def _get_company(self,data):
		user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
		return user and user.company_id or False

	def _get_warehouse(self,data):
		warehouse = self.pool.get('stock.warehouse').browse(self.cr, self.uid, self.uid)
		return warehouse and warehouse.company_id or False


	def _get_attns(self, cust):
		attns_lst = ' '
		if cust:
			attns_lst += cust.name or ''
		if cust and cust.child_ids:
			for child_cust in cust.child_ids:
				attns_lst += ', ' + child_cust.name or ''
		return attns_lst


class report_print_sales_register_pdf_extended(models.AbstractModel):
	_name = 'report.stspl_sales.stspl_sales_partner_account_statement_template'
	_inherit = 'report.abstract_report'
	_template = 'stspl_sales.stspl_sales_partner_account_statement_template'
	_wrapped_report_class = report_partner_account_statement