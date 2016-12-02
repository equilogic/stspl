# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services Pvt. Ltd. (<http://serpentcs.com>).
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
    "name": "STSPL Sales",
    "version": "1.1",
    "depends": ['sale','sg_account',],
    "author" :"Serpent Consulting Services Pvt. Ltd.",
    "website" : "http://www.serpentcs.com",
    "category": "sales",
    "description":"""
        This module customises the sales reports as per the Customs of STSPL.
    """,
    "data": [
             'data/account_payment_terms_demo.xml',
             'views/stock_picking.xml',  
	         'report/sale_delivery_order_report_view.xml',
             'views/company_view.xml',
             'report/sale_order_report_view.xml',
             'views/report_view.xml',
             'data/ir.sequence.xml',
             'views/sale_order_view.xml',
             
    ],
    "installable": True,
    "auto_install":False,
    "application":False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
