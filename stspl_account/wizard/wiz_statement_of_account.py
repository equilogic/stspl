from openerp import fields,models,api
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
import time
from openerp import tools

class statement_of_account(models.TransientModel):
    _name = 'statement.of.account'
    

    customer_ids = fields.Many2many('res.partner',
                                        'statement_account_rel', 'soa_id',
                                        'customer_id', 'Customers')
    start_date = fields.Date('Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    page_split = fields.Boolean('One Customer Per Page', help='Display Report with One Customer per page', default=True)



    @api.multi
    def print_report(self):
        
        partner_obj = self.env['res.partner']
        for value in self:

            if self._context is None:
                self._context= {}
            datas = {
                'ids':self.ids,
                'model':'statement.of.account',
            }
            res = self.read([])
            res = res and res[0] or {}
            if not res.get('customer_ids'):
                cust_ids = partner_obj.search([('customer', '=', True)])
                if cust_ids:
                    res['customer_ids'] = cust_ids
            datas['form'] = res
        print":::::::::::::::::::::::::",datas
        return self.env['report'].get_action(self,
                 'stspl_account.stspl_account_statement_of_account_template', data = datas)



