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

class order_summary_xls_report(models.TransientModel):
    _name = 'order.summary.xls'




    @api.multi
    def print_xls_export(self):        
        cr,uid,context = self.env.args

        fl = StringIO()
        cr,uid,context=self.env.args
        ctx=dict(context)


        max_raw=0
        min_raw=1
           
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('New Sheet')
              
        font = xlwt.Font()
        font.bold = True

        row=10        
        col=0

        align_left = xlwt.easyxf('align: horiz left,vert center')
        align_right = xlwt.easyxf('align: horiz right,vert center')
        align_center = xlwt.easyxf('align: horiz center,vert center')
        color_yellow = xlwt.easyxf('borders :top hair, bottom hair, bottom_color black,top_color black;'
                            'pattern:pattern solid ,fore_colour yellow;')
        color_green = xlwt.easyxf('borders :top hair, bottom hair, bottom_color black,top_color black;'
                            'pattern:pattern solid ,fore_colour green;')
        color_blue = xlwt.easyxf('borders :top hair, bottom hair, bottom_color black,top_color black;'
                            'pattern:pattern solid ,fore_colour dark_blue;')


        worksheet.write_merge(9,9,0,0, 'CUSTOMER',color_yellow)
        worksheet.write_merge(9,9,1,1,'',color_yellow)
        worksheet.write_merge(9,9,2,2,'',color_yellow)
        worksheet.write_merge(9,9,3,3,'',color_yellow)
        worksheet.write_merge(9,9,4,4,'',color_yellow)
        worksheet.write_merge(9,9,5,5,'',color_yellow)
        worksheet.write_merge(9,9,6,6,'',color_yellow)
        worksheet.write_merge(9,9,7,7,'',color_yellow)
        worksheet.write_merge(9,9,8,8,'USD/SGD',color_yellow)
        worksheet.write_merge(9,9,9,9,'',color_yellow)
        worksheet.write_merge(9,9,10,10,'',color_yellow)
        worksheet.write_merge(9,9,11,11,'',color_yellow)
        worksheet.write_merge(9,9,12,12,'',color_yellow)
        worksheet.write_merge(9,9,13,13,'',color_yellow)
        worksheet.write_merge(9,9,14,14,'',color_yellow)

        worksheet.write_merge(9,9,15,15,'SUPPLIER',color_green)
        worksheet.write_merge(9,9,16,16,'',color_green)
        worksheet.write_merge(9,9,17,17,'SGD/USD',color_green)
        worksheet.write_merge(9,9,18,18,'',color_green)
        worksheet.write_merge(9,9,19,19,'',color_green)
        worksheet.write_merge(9,9,20,20,'',color_green)
        worksheet.write_merge(9,9,21,21,'',color_green)
        worksheet.write_merge(9,9,22,22,'',color_green)


        worksheet.write_merge(9,9,23,23,'INTERNAL PURPOSES ONLY',color_blue)
        worksheet.write_merge(9,9,24,24,'',color_blue)
        worksheet.write_merge(9,9,25,25,'',color_blue)
        worksheet.write_merge(9,9,26,26,'',color_blue)
        worksheet.write_merge(9,9,27,27,'',color_blue)
        worksheet.write_merge(9,9,28,28,'',color_blue)
        worksheet.write_merge(9,9,29,29,'',color_blue)



        worksheet.row(1).height=400
        worksheet.row(row).height=400
        worksheet.row(row+1).height=400
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 10000
        worksheet.col(3).width = 4000
        worksheet.col(4).width = 3000
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 11000
        worksheet.col(7).width = 4000
        worksheet.col(8).width = 4000
        worksheet.col(9).width = 5000
        worksheet.col(10).width = 4000
        worksheet.col(11).width = 4000
        worksheet.col(12).width = 4000
        worksheet.col(13).width = 5500
        worksheet.col(14).width = 3500
        worksheet.col(15).width = 4000
        worksheet.col(16).width = 4000
        worksheet.col(17).width = 5000
        worksheet.col(18).width = 5000
        worksheet.col(19).width = 5000
        worksheet.col(20).width = 5000
        worksheet.col(21).width = 5000
        worksheet.col(22).width = 5000
        worksheet.col(23).width = 5000
        worksheet.col(24).width = 5000
        worksheet.col(25).width = 11000
        worksheet.col(26).width = 8000
        worksheet.col(27).width = 5000
        worksheet.col(28).width = 6000
        worksheet.col(29).width = 12000



        worksheet.write(row, col, "PO#")
        col+=1
        worksheet.write(row, col, "PO DATE")
        col+=1
        worksheet.write(row, col, "CUSTOMER")
        col+=1
        worksheet.write(row, col, "REQUESTER")
        col+=1
        worksheet.write(row, col, "QTY")
        col+=1
        worksheet.write(row, col, "ITEM/ACCT")
        col+=1
        worksheet.write(row, col, "DESCRIPTION")
        col+=1
        worksheet.write_merge(10,10,7,8, "ORIGINAL SELLING PRICE")
        col+=2
        worksheet.write(row, col, "TOTAL AMOUNT")
        col+=1
        worksheet.write(row, col, "QUETE#")
        col+=1
        worksheet.write(row, col, "SALES")
        col+=1
        worksheet.write(row, col, "CITY")
        col+=1
        worksheet.write(row, col, "STSPL P/N")
        col+=1
        worksheet.write(row, col, "STATUS")
        col+=1
        worksheet.write(row, col, "VENDOR")
        col+=1
        worksheet.write(row, col, "PO#")
        col+=1
        worksheet.write(row, col, "PO DATE#")
        col+=1
        worksheet.write(row, col, "SUPPLIER QUOTE#")
        col+=1
        worksheet.write(row, col, "SUPPILER P/N")
        col+=1
        worksheet.write(row, col, "SUPPILER INV")
        col+=1
        worksheet.write(row, col, "CURR")
        col+=1
        worksheet.write(row, col, "BUY PRICE UNIT")
        col+=1
        worksheet.write(row, col, "INV#")
        col+=1
        worksheet.write(row, col, "INV DATE")
        col+=1
        worksheet.write(row, col, "SHIPPING DETAIL / INCOMMING ")
        col+=1
        worksheet.write(row, col, "DIMENSIONS / INCOMMING")
        col+=1
        worksheet.write(row, col, "GROSSS WT")
        col+=1
        worksheet.write(row, col, "FREIGHT CHARGES")
        col+=1
        worksheet.write(row, col, "REMARKS / DEVIVER")
        col+=1



        row=11
        col=0
        customer = self.env['res.partner'].search([('customer', '=', True)])
        if customer:
            sale_order_lines = self.env['sale.order.line'].search([('order_id.partner_id', 'in', customer.ids)])

            for data in sale_order_lines:

                worksheet.row(row).height=400
                worksheet.write(row, col, data.order_id.name  or '')
                col+=1
                worksheet.write(row, col, data.order_id.date_order  or '')
                col+=1
                worksheet.write(row, col, data.order_id.partner_id.name  or '')
                col+=1
                worksheet.write(row, col, data.order_id.attn_sales or '')
                col+=1
                worksheet.write(row, col,data.product_uom_qty or '')
                col+=1
                worksheet.write(row, col,data.product_id.default_code or '')
                col+=1
                worksheet.write(row, col,data.name or '')
                col+=1
                worksheet.write(row, col,data.order_id.company_id.currency_id.name)
                col+=1
                worksheet.write(row, col,data.price_unit or '')
                col+=1
                worksheet.write(row, col, data.price_subtotal or'')
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                row+=1
                col=0  



        row=11
        col=15
        supplier = self.env['res.partner'].search([('supplier', '=', True)])

        if supplier:
            purchase_ids = self.env['purchase.order'].search([('partner_id', 'in', supplier.ids)])

            for data in purchase_ids:

                worksheet.row(row).height=400
                worksheet.write(row, col, data.partner_id.name  or '')
                col+=1
                worksheet.write(row, col, data.name  or '')
                col+=1
                worksheet.write(row, col, data.date_order  or '')
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,data.partner_id.company_id.currency_id.name or'')
                col+=1
                worksheet.write(row, col, data.amount_total or'')
                col+=1
                row+=1
                col=15 


        row=11
        col=23
        cust_invoice = self.env['res.partner'].search([('customer', '=', True)])

        if cust_invoice:
            invoice_id = self.env['account.invoice'].search([('partner_id', 'in', cust_invoice.ids)])

            for data in invoice_id:

                worksheet.row(row).height=400
                worksheet.write(row, col, data.number  or '')
                col+=1
                worksheet.write(row, col, data.date_invoice  or '')
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                worksheet.write(row, col,)
                col+=1
                row+=1
                col=23 
                      


        workbook.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx.update({'file':buf})
        return {
            'name': 'Attatchment',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'order.summary.xls.export',
            'target': 'new',
            'context': ctx
        }


class order_summary_xls_export(models.TransientModel):
    _name = "order.summary.xls.export"

    file = fields.Binary('File')
    name = fields.Char(string='File Name', size=64)

    @api.model
    def default_get(self, fields):
        super(order_summary_xls_export, self).default_get(fields)
        cr, uid, context = self.env.args
        res = dict(context)
        vals = {'name': 'Order Summary Xls Report.xls'}
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
    def click_back(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'order.summary.xls',
            'target': 'new',
        }