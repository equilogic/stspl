from openerp import models,fields,api
import base64
import tempfile
import xlrd
from xlrd import open_workbook
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.tools import  DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta


class wiz_xls_import(models.TransientModel):

    _name='wiz.xls.import'

    xls_file = fields.Binary('File')
    datas_fname = fields.Char(string='File Name', size=64)


    @api.multi
    def xls_import(self):
        cr, uid, context = self.env.args
        for rec in self:
            datafile = rec.xls_file
            file_name = str(rec.datas_fname)
            # Checking for Suitable File
            if not datafile or not file_name.lower().endswith(('.xls', '.xlsx',)):
                raise Warning(_("Please Select an .xls or its compatible file to Import"))
            xls_data = base64.decodestring(datafile)
            temp_path = tempfile.gettempdir()
            # writing a file to temp. location
            fp = open(temp_path + '/xsl_file.xls', 'wb+')
            fp.write(xls_data)
            fp.close()
            # opening a file form temp. location
            wb = open_workbook(temp_path + '/xsl_file.xls')
            data_list = []
            headers_dict = {}
            supplier_dict = {}
            company_dict = {}
            currency_dict = {}
                        
            for sheet in wb.sheets():
                for rownum in range(sheet.nrows):
                    # Preparing headers
                    if rownum == 0:
                        # converting unicode chars. into string
                        header_list = [x.strip().encode('UTF8') for x in sheet.row_values(rownum)]
                        fixed_list = ['Supplier Name', 'Order Date', 'Shipment Term', 'Ship Via', 'Product Name',
                                         'Item Reference', 'Po Qty', 'Unit Price']
                        # Comparing columns of Existing List With Columns of Uploaded (.xls) File's
                        for column in fixed_list:
                                if column not in header_list:
                                    raise Warning(_("Column Named = '%s' Not Found in Uploaded File." \
                                                    "\n Please Upload The File Having At least Columns like :- %s" \
                                                     % (column, fixed_list)))
                        headers_dict = {
                                    'supplier_name'         : header_list.index('Supplier Name'),
                                    'order_date'            : header_list.index('Order Date'),
                                    'shipment_term'         : header_list.index('Shipment Term'),
                                    'ship_via'              : header_list.index('Ship Via'),
                                    'product_name'          : header_list.index('Product Name'),
                                    'item_ref'              : header_list.index('Item Reference'),
                                    'po_qty'                : header_list.index('Po Qty'),
                                    'unit_price'            : header_list.index('Unit Price'),
                                }

                    if rownum >= 1:
                        data_list.append(sheet.row_values(rownum))

            if data_list and headers_dict:           

                for row in data_list:
                    s_name            =  row[headers_dict['supplier_name']]
                    s_o_date          =  row[headers_dict['order_date']]
                    s_term            =  row[headers_dict['shipment_term']]
                    s_via             =  row[headers_dict['ship_via']]
                    s_prod_name       =  row[headers_dict['product_name']]
                    s_item_ref        =  row[headers_dict['item_ref']]
                    s_po_qty          =  row[headers_dict['po_qty']]
                    s_unit_price      =  row[headers_dict['unit_price']]


                    if context.get('active_id', False):
                        purchase_rec = self.env['purchase.order'].browse(context['active_id'])

                        flag=False

                        for line in purchase_rec.order_line:
                            if line.product_id.default_code == s_item_ref:                    
                                line.write({'product_qty':s_po_qty,'price_unit':s_unit_price})
                                
                                flag=True
                        if not flag:
                            product = self.env['product.product'].search([('default_code','=',s_item_ref)])
                            line =({'product_id':product and product.ids[0] or False,
                                    'name': product and product[0].name or '',
                                    'product_qty':s_po_qty,
                                    'price_unit':s_unit_price,
                                    'order_id':purchase_rec.id,
                                    'date_planned':purchase_rec and purchase_rec.date_order or False
                                })
                            final = self.env['purchase.order.line'].create(line) 
            return True



                
  