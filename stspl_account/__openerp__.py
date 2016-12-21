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

{
    'name': 'STSPL Account',
    'version': '1.1',
    'depends': ['purchase','sg_account_odoo'],
    'author' :'Serpent Consulting Services Pvt. Ltd.',
    'website' : 'http://www.serpentcs.com',
    'category': 'purchase',
    'description':"""
            This module customises the accounting reports as per the Customs of STSPL.
    """,
    
    'data': [
             'views/account_invoice_view.xml',
             'views/report_view.xml',
             'views/res_partner_view.xml',
             'report/stspl_tax_invoice_report_view.xml',
             'report/packing_list.xml',
             'report/sale_acknowledge_report.xml',
             'report/stspl_proforma_report.xml',
             'report/statement_of_account_view.xml',
             'report/customer_payment_report_view.xml',
             'report/bank_reconcilication.xml',
             'data/ir.sequence_tax.xml',
             'wizard/wiz_statement_of_account_view.xml',
             
    ],
    'installable': True,
    'auto_install':False,
    "application":False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
