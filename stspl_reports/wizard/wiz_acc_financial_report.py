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

from openerp import fields, models, api
from openerp.tools.translate import _


class wizard_report(models.TransientModel):
    _inherit = "wizard.report"

    @api.model
    def default_get(self, fields):
        res = super(wizard_report, self).default_get(fields)
        if self._context and self._context.get('inf_type', False):
            res.update({'inf_type': self._context['inf_type']})
        return res

    @api.v7
    def onchange_inf_type(self, cr, uid, ids, inf_type, context=None):
        if context is None:
            context = {}
        res = {'value':{}, 'domain':{}}
        if inf_type:
            res['domain'].update(
                {'afr_id': [('inf_type', '=', inf_type)]})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

