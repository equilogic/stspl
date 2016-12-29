from openerp import fields,models,api
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
import time
from openerp import tools


from openerp import models,fields,api
import xlwt
import base64
import tempfile
from xlrd import open_workbook
from StringIO import StringIO
from datetime import datetime
from openerp.tools import misc, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.sql import drop_view_if_exists

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
        return self.env['report'].get_action(self,
                 'stspl_account.stspl_account_statement_of_account_template', data = datas)



    
    @api.multi
    def print_xls_export(self):        
        cr,uid,context = self.env.args

        fl = StringIO()
        cr,uid,context=self.env.args
        ctx=dict(context)


        max_raw=0
        min_raw=1
           
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('New Sheet')
              
        font = xlwt.Font()
        font.bold = True


        header_date_1 = xlwt.easyxf('align: horiz center,vert center ;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black')
        header_date_2 = xlwt.easyxf('font: bold 1, height 230; align: horiz center,vert center ,wrap 1;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black')

        align_right = xlwt.easyxf('align: horiz right,vert center')
        align_left = xlwt.easyxf('align: horiz left,vert center')
        align_center = xlwt.easyxf('align: horiz center,vert center')
        company_name = xlwt.easyxf('font: bold 1, height 270; align: horiz right,vert center')




        partner_data = self.get_start_partners()
        print "partner_data:::::::::::::::::::::::::::::::::",partner_data

        for partner in partner_data.get('list',[]):

            worksheet.write_merge(0,4,0,1, base64.b64encode(partner.company_id.logo))
            worksheet.write_merge(0,1,3,5, partner.company_id.name or '',company_name)
            worksheet.write_merge(2,2,3,5, partner.company_id.street or '',align_right)
            worksheet.write_merge(3,3,3,5, partner.company_id.city or '',align_right)
            worksheet.write_merge(4,4,3,5, partner.company_id.state_id.name or '',align_right)
            worksheet.write_merge(5,5,3,5, partner.company_id.country_id.name or '',align_right)
            worksheet.write_merge(6,6,3,5, partner.company_id.zip or '',align_right) 
            worksheet.write_merge(7,7,3,5, 'TEL :' + partner.company_id.phone + '     ' + 'FAX :' +partner.company_id.fax,align_right)
            worksheet.write_merge(8,8,3,5, 'CO. REG. NO. :' + partner.company_id.company_registry or '',align_right)
            worksheet.write_merge(9,9,3,5, 'GST REG NO. :' + partner.company_id.gst_no or '',align_right)


            worksheet.write_merge(7,9,0,1, 'STATEMENT OF ACCOUNT', header_date_2)
            worksheet.write_merge(11,11,0,1, partner.name or '')
            worksheet.write_merge(12,12,0,1, partner.house_no or '')
            worksheet.write_merge(13,13,0,1, partner.street or '') 
            worksheet.write_merge(14,14,0,1, partner.street2 or '')
            worksheet.write_merge(15,15,0,1, partner.level_no or '')
            worksheet.write_merge(16,16,0,1, partner.state_id.name or '')
            worksheet.write_merge(17,17,0,1, partner.country_id.name or '')
            worksheet.write_merge(18,18,0,1, partner.zip or '')
            worksheet.write_merge(19,19,0,1, 'ATTN :')
            worksheet.write_merge(20,20,0,3, 'TEL :' + partner.phone + '                                   ' + 'FAX :' + partner.fax or '') 


            worksheet.write_merge(22,23,0,1, 'CURRENCY' + '\n' + partner.company_id.currency_id.name or '',header_date_2)
            worksheet.write_merge(22,23,2,3, 'TERM' + '\n' + partner.property_payment_term.name or '',header_date_2)
            worksheet.write_merge(22,23,4,5, 'FOR THE MONTH OF' + '\n' + self.get_date() or '',header_date_2)


            row=25
            col=0
            worksheet.row(1).height=400
            worksheet.row(row).height=550
            worksheet.col(0).width = 5000
            worksheet.col(1).width = 5000
            worksheet.col(2).width = 4500
            worksheet.col(3).width = 4000
            worksheet.col(4).width = 5000
            worksheet.col(5).width = 5000

            
            worksheet.write(row, col, "DATE",header_date_2)
            col+=1
            worksheet.write(row, col, "INOICE NO.",header_date_2)
            col+=1
            worksheet.write(row, col, "AMOUNT($)",header_date_2)
            col+=1
            worksheet.write(row, col, "DUE DATE",header_date_2)
            col+=1
            worksheet.write(row,col,"AGING",header_date_2)
            col+=1
            worksheet.write(row,col,"OUTSTANDING BALANCE($)",header_date_2)
            col+=1
            row+=1


        lines_data = self.lines()
        for lines in lines_data:  
            worksheet.row(row).height=400
            col=0
            worksheet.write(row, col, lines['date'],header_date_1)
            col+=1
            worksheet.write(row, col, lines['inv_no'],header_date_1)
            col+=1
            worksheet.write(row, col, lines['debit'],header_date_1)
            col+=1
            worksheet.write(row, col, lines['due_date'],header_date_1)
            col+=1
            worksheet.write(row, col, lines['due_date'],header_date_1)
            col+=1
            worksheet.write(row, col, lines['total'],header_date_1)
            col+=1
            row+=1            


        row=51
        col=0
        worksheet.row(1).height=400
        worksheet.row(row).height=550
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 4500
        worksheet.col(3).width = 4000
        worksheet.col(4).width = 5000

        worksheet.write(row, col, ">90 DAYS ",header_date_2)
        col+=1
        worksheet.write(row, col, "60 - 90 DAYS",header_date_2)
        col+=1
        worksheet.write(row, col, "30 - 60 DAYS",header_date_2)
        col+=1
        worksheet.write(row, col, "<30 DAYS ",header_date_2)
        col+=1
        worksheet.write(row,col,"CURRENT",header_date_2)
        col+=1
        row+=1

        # date_part_data = self.date_part()
        # print" date_part_data::::::::::::::::::::::::"
        # for s_part in date_part_data:
        worksheet.row(row).height=400
        col=0
        worksheet.write(row, col, '' ,header_date_1)
        col+=1
        worksheet.write(row, col, '' ,header_date_1)
        col+=1
        worksheet.write(row, col, '' ,header_date_1)
        col+=1
        worksheet.write(row, col, '' ,header_date_1)
        col+=1
        worksheet.write(row, col, self.get_all_total(),header_date_1)
        col+=1
        row+=1

        worksheet.write_merge(53,55,0,5, 'This is a computer generated documents and no signature is required' + '\n' + '\n' +'Email:' + partner.company_id.email + '             ' + 'Website:' + partner.company_id.website,align_center)

        workbook.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx.update({'file':buf})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.stspl.xls.export',
            'target': 'new',
            'context': ctx
        }


    @api.multi
    def get_date(self):
        data_data = {}
        if self.start_date:
            date = datetime.strptime(self.start_date,DEFAULT_SERVER_DATE_FORMAT)
            data_data = datetime.strftime(date, "%d-%m-%Y")        
        return data_data

    
    @api.multi
    def get_start_partners(self):
        partner_obj = self.env['res.partner']
        lst = []
        result={}
        attn_dict={}
        data = []
        self.start_date
        data2 = []
        if self.customer_ids:
            for partner in self.customer_ids:
                date_data = self.date_part(partner)
                for key, value in date_data[0].items():
                    data2 = self.get_move_data(value['start'], value['stop'], partner)
                    if data2:
                        if partner not in lst:
                            lst.append(partner)
                            attn_id = partner_obj.search([('parent_id','=',partner.id),('type','=','other')])
                            attn_dict.update({partner:attn_id and attn_id[0].name or ''})
            result.update({'list':lst,'attn':attn_dict})
        return result



    @api.multi
    def lines(self):
        partner = self.env['res.partner'].search([])
        inv_list = []
        total = 0.0
        inv_id_list = []
        if partner:
            inv_ids = self.env['account.invoice'].search([('partner_id', '=', partner.ids),
                                                                     ('state', 'not in', ('draft', 'cancel', 'paid')),
                                                                     ('type', 'in', ('out_invoice', 'out_refund')),
                                                                     ('date_invoice', '<=', self.start_date),
                                                                     ], order = 'date_invoice desc')                         
            if inv_ids:
                for inv_data in inv_ids:
                    inv_dict = {}
                    date_invoice_format = ''
                    date_due_format = ''
                    if inv_data.type == 'out_invoice':
                        total += inv_data.residual
                        inv_dict.update({'debit': inv_data.residual and inv_data.residual or 0.0})
                        inv_dict.update({'credit': 0.0})
                        if inv_data.payment_ids:
                            debit = 0.0
                            credit = 0.0
                            for payment_rec in inv_data.payment_ids:
                                if inv_data.company_id.currency_id.id != inv_data.currency_id.id:
                                    credit += abs(payment_rec.amount_currency)
                                else:
                                    credit += payment_rec.credit
                                inv_dict.update({'credit':credit or 0.0})
                                inv_dict.update({'debit': inv_data.residual and inv_data.residual or 0.0})
                    if inv_data.type == 'out_refund':
                        total -= inv_data.residual
                        debit = 0.0
                        inv_dict.update({'credit': inv_data.residual and inv_data.residual or 0.0})
                        for payment_rec in inv_data.payment_ids:
                                if inv_data.company_id.currency_id.id != inv_data.currency_id.id:
                                    debit -= abs(payment_rec.amount_currency)
                                else:
                                    debit += payment_rec.credit                            
                                inv_dict.update({'debit': debit or 0.0})
                    if inv_data.date_invoice:
                        converted_date = datetime.strptime(inv_data.date_invoice, DEFAULT_SERVER_DATE_FORMAT)
                        date_invoice_format = datetime.strftime(converted_date, "%d-%m-%Y")

                    if inv_data.date_due:
                        converted_date = datetime.strptime(inv_data.date_due, DEFAULT_SERVER_DATE_FORMAT)
                        date_due_format = datetime.strftime(converted_date, "%d-%m-%Y")

                    inv_dict.update({
                                     'date': date_invoice_format,
                                     'inv_no': inv_data.number,
                                     'due_date':date_due_format,
                                     'total': total})
                    inv_list.append(inv_dict)

        self.all_inv_total = total
        return inv_list


    @api.multi
    def get_all_total(self):
        return self.all_inv_total
    

    def date_part(self, partner):
        res = {}
        date_data = []
        start = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
        for i in range(4)[::-1]:
            stop = start - relativedelta(days=30)
            try:
                res[str(i)] = {
                    'name': (i != 0 and (str((4 - (i + 1)) * 30) + '-' + str((4 - i) * 30)) or ('' + str(3 * 30))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
                }
            except Exception as ex:
                raise except_orm(_('User Error'), _('Please select Valid date'))
            start = stop - relativedelta(days=1)
        date_data.append(res)
        return date_data

    
    def get_move_data(self, date_s, date_e, partner):
        inv_ids = []
        if partner and date_s and date_e:
            inv_ids = self.env['account.invoice'].search([('partner_id', '=', partner.id),
                                                                         ('state', 'not in', ('draft', 'cancel', 'paid')),
                                                                         ('type', 'in', ('out_invoice', 'out_refund')),
                                                                         ('date_due', '<=', date_e),
                                                                         ('date_due', '>=', date_s), ])
        if partner and not date_s:
            if inv_ids:
                inv_ids.append(self.env['account.invoice'].search([('partner_id', '=', partner.id),
                                                                         ('state', 'not in', ('draft', 'cancel', 'paid')),
                                                                         ('type', '=', 'out_invoice'),
                                                                         ('date_due', '<=', date_e),
                                                                         ],)) 
            else:
                inv_ids = self.env['account.invoice'].search([('partner_id', '=', partner.id),
                                                                         ('state', 'not in', ('draft', 'cancel', 'paid')),
                                                                         ('type', 'in', ('out_invoice', 'out_refund')),
                                                                         ('date_due', '<=', date_s),
                                                                         ],)               
        amt = 0.0
        if inv_ids:
            for inv_data in inv_ids:
                if inv_data.type =='out_invoice':
                    amt += inv_data.residual
                if inv_data.type =='out_refund':
                    amt -= inv_data.residual
        return amt



class wizard_stspl_xls_export(models.TransientModel):
    _name = "wizard.stspl.xls.export"

    file = fields.Binary('File')
    name = fields.Char(string='File Name', size=64)

    @api.model
    def default_get(self, fields):
        super(wizard_stspl_xls_export, self).default_get(fields)
        cr, uid, context = self.env.args
        res = dict(context)
        vals = {'name': 'Statement Of Account Xls Export Report.xls'}
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
    def button_back(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'statement.of.account',
            'target': 'new',
        }





