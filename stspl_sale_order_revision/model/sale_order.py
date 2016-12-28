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

from openerp import fields, models, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class sale_order(models.Model):
    _inherit = "sale.order"

    curr_rev_id = fields.Many2one('sale.order', 'Current revision', copy=True)
    old_rev_ids = fields.One2many('sale.order', 'curr_rev_id', 'Old revisions', context={'active_test': False})
    rev_number = fields.Integer('Revision', copy=False)
    unrevisioned_ref = fields.Char('Order Reference', copy=True)
    active = fields.Boolean('Active', default=True, copy=True)
    state = fields.Selection([
            ('draft', 'Draft Quotation'), ('sent', 'Quotation Sent'), ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'), ('progress', 'Sales Order'), ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'), ('invoice_except', 'Invoice Exception'),
            ('revised', 'Revised / Edited'),('pending', 'Pending'),
            ('negotiation', 'Negotiation'),('done', 'Done')], 'Status',
            readonly=True, copy=False,
            help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True)


    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_ref, rev_number, company_id)',
         'Order Reference and revision must be unique per Company.'),
    ]
    
    @api.multi
    def action_revised(self):
        for rec in self:
            rec.state = 'revised'
        return True
    
    @api.multi
    def action_negotiation(self):
        for rec in self:
            rec.state = 'negotiation'
        return True

    @api.multi
    def action_pending(self):
        for rec in self:
            rec.state = 'pending'
        return True

    @api.multi
    def copy_quotation(self):
        self.ensure_one()
        revision_self = self.with_context(new_sale_rev=True)
        action = super(sale_order, revision_self).copy_quotation()
        old_revision = self.browse(action['res_id'])
        action['res_id'] = self.id
        self.delete_workflow()
        self.create_workflow()
        self.write({'state': 'draft'})
        self.order_line.write({'state': 'draft'})
        # remove old procurements
        self.mapped('order_line.procurement_ids').write(
            {'sale_line_id': False})
        msg = _('New revision created: %s') % self.name
        self.message_post(body=msg)
        old_revision.message_post(body=msg)
        return action

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('new_sale_rev'):
            prev_name = self.name
            revno = self.rev_number
            self.write({'rev_number': revno + 1,
                        'name': '%s-%02d' % (self.unrevisioned_ref,
                                             revno + 1)
                        })
            defaults.update({'name': prev_name,
                             'rev_number': revno,
                             'active': False,
                             'state': 'cancel',
                             'curr_rev_id': self.id,
                             'unrevisioned_ref': self.unrevisioned_ref,
                             })
        return super(sale_order, self).copy(defaults)

    @api.model
    def create(self, values):
        if 'unrevisioned_ref' not in values:
            if values.get('name', '/') == '/':
                seq = self.env['ir.sequence']
                values['name'] = seq.next_by_code('sale.order') or '/'
            values['unrevisioned_ref'] = values['name']
        return super(sale_order, self).create(values)


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.depends('product_id','product_id.standard_price','product_uom_qty','purchase_price','price_unit')
    def _product_margin(self):
        cur_obj = self.env['res.currency']
        res = {}
        for line in self:
            cur = line.order_id.pricelist_id.currency_id
            line.margin = 0
            cost_price = 0
            if line.product_id:
                prod = line.product_id
                cost_price += line.purchase_price or line.product_id.standard_price or 0.0
                cost_price += (prod.markup_amt + prod.shipment_amt + prod.operation_amt + prod.expense_amt + prod.pure_profit_amt)
                tmp_margin = line.price_subtotal - ((cost_price) * line.product_uos_qty)
                line.margin = cur.round(tmp_margin)

    margin = fields.Float(compute=_product_margin, string='Margin',
                          digits_compute= dp.get_precision('Product Price'),
                          store=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: