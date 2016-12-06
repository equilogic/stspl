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
    'name': 'STSPL Purchase Reports',
    'version': '1.1',
    'depends': ['purchase','sg_account'],
    'author' :'Serpent Consulting Services Pvt. Ltd.',
    'website' : 'http://www.serpentcs.com',
    'category': 'purchase',
    'description':"""
            This module customises the purchase reports as per the Customs of STSPL.
    """,
    
    'data': [
             'report/stspl_purchase_report_view.xml',
             'views/report_view.xml',
             'views/purchase_order_view.xml',
             'data/ir.sequence_tax.xml',
             
    ],
    'installable': True,
    'auto_install':False,
    "application":False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
