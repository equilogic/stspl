from openerp import models,fields,api

import xlwt
import base64
import tempfile
from xlrd import open_workbook
from StringIO import StringIO
from datetime import datetime
from openerp.tools import misc, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.sql import drop_view_if_exists


class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    
    @api.multi
    def print_report(self):        
        cr,uid,context = self.env.args

        fl = StringIO()
        cr,uid,context=self.env.args
        ctx=dict(context)

        row=0
        col=0

        max_raw=0
        min_raw=1
           
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('New Sheet')
              
        font = xlwt.Font()
        font.bold = True
        data_style = xlwt.easyxf('font: height 200; borders: top hair, bottom hair,left hair, right hair, bottom_color black,top_color black ,right_color black,left_color black;align: wrap off;align: wrap on , horiz left;')
        
        header1 = xlwt.easyxf('align: horiz center,vert center ;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black')
        header2 = xlwt.easyxf('font: bold 1, height 230; align: horiz center,vert center ,wrap 1;borders :top hair, bottom hair,left hair, right hair, bottom_color black,top_color black')
          
        worksheet.row(1).height=400
        worksheet.row(row).height=400
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 4500
        worksheet.col(3).width = 4000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 5000
        worksheet.col(7).width = 4000
        
        worksheet.write(row, col, "Supplier Name",header2)
        col+=1
        worksheet.write(row, col, "Order Date",header2)
        col+=1
        worksheet.write(row, col, "Shipment Term",header2)
        col+=1
        worksheet.write(row, col, "Ship Via",header2)
        col+=1
        worksheet.write(row,col,"Product Name",header2)
        col+=1
        worksheet.write(row,col,"Item Reference",header2)
        col+=1
        worksheet.write(row,col,"Po Qty",header2)
        col+=1
        worksheet.write(row,col,"Unit Price",header2)
        col+=1
        row+=1
               
        purchase_ids = self.env['purchase.order'].search([])
        for p_line in self.order_line:
            worksheet.row(row).height=400
            col=0
            worksheet.write(row, col, self.partner_id and self.partner_id.name or '',header1)
            col+=1
            worksheet.write(row, col, self.date_order or '',header1)
            col+=1
            worksheet.write(row, col, self.date_order or '',header1)
            col+=1
            worksheet.write(row, col, self.ship_via_id and self.ship_via_id.name or '',header1)
            col+=1
            worksheet.write(row, col, p_line.product_id and p_line.product_id.name or '' ,header1)
            col+=1
            worksheet.write(row, col, p_line.product_id and p_line.product_id.default_code or '',header1)
            col+=1
            worksheet.write(row, col, p_line.product_qty or 0.0,header1)
            col+=1
            worksheet.write(row, col, p_line.price_unit or 0.0,header1)
            col+=1
            row+=1
        workbook.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx.update({'file':buf})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.stspl.xls.export',
            'target': 'new',
            'context': ctx
        }

class wiz_stspl_xls_export(models.TransientModel):
    _name = "wiz.stspl.xls.export"

    file = fields.Binary('File')
    name = fields.Char(string='File Name', size=64)

    @api.model
    def default_get(self, fields):
        super(wiz_stspl_xls_export, self).default_get(fields)
        cr, uid, context = self.env.args
        res = dict(context)
        vals = {'name': 'purchase Quotation Report.xls'}
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