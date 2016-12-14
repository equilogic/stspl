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
                        # print"headers_dict::::::::::::::::::::::::::::::::::;",headers_dict
                    if rownum >= 1:
                        data_list.append(sheet.row_values(rownum))
            print "headers_dict::::::::::::::::::::::::::::",headers_dict
            if data_list and headers_dict:
                # Collecting Projects in dictionary
                # having key as project name and project id as a value.
                print "\n data_list :::::::::::", data_list

                # cr.execute("select rp.name,ru.id from res_users ru,res_partner rp \
                #                      where rp.id = ru.partner_id ")
                # supplier_dict.update(cr.fetchall())
                # print ":::::::::::::::::::::::::::::::::::::::supplier_dict",supplier_dict

                for row in data_list:
                    print "\n row ::::::::::::::", row
                    s_name            =  row[headers_dict['supplier_name']]
                    s_date            =  row[headers_dict['order_date']]
                    s_term            =  row[headers_dict['shipment_term']]
                    s_via             =  row[headers_dict['ship_via']]
                    s_prod_name       =  row[headers_dict['product_name']]
                    s_item_ref        =  row[headers_dict['item_ref']]
                    s_po_qty          =  row[headers_dict['po_qty']]
                    s_unit_price      =  row[headers_dict['unit_price']]

                    print "\n s_name ::::::::::", s_name
                    supplier = False
                    if s_name:
                        supplier = self.env['res.partner'].search([('name','=', s_name),('supplier','=', True)], limit=1)
                    else:
                        supplier = self.env['res.partner'].create({'name': s_name, 'supplier': True})

                    purchase_vals = {'partner_id': supplier and supplier.id or False}
                    pick_type = self.env['stock.picking.type'].search([('code','=', 'incoming'),('warehouse_id.company_id','=', supplier and supplier.company_id.id or False)], limit=1)

                    print "\n pick_type :::::::::", pick_type
                    if pick_type:
                        purchase_vals.update({'picking_type_id': pick_type and pick_type.id or False, 'location_id': pick_type and pick_type.default_location_dest_id.id or False})
                    new_purch_id = self.env['purchase.order'].create(purchase_vals)
                    print "\n new_purch_id :::::::::::", new_purch_id




                #     pur_order_id = False


                #     if s_name:
                #         if s_name in supplier_dict:
                #             pur_order_id = supplier_dict[s_name]


                #     if not pur_order_id:

                #         create_datetime = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)

                #         pur_order_qry = "insert into purchase_order \
                #                 (create_uid,create_date"

                #         pur_order_params = (uid, create_datetime)

                #         pur_order_values = "%s, %s"

                #         # order Date
                #         if type (s_date) == float:
                #                     dt = datetime(* (xlrd.xldate_as_tuple(s_date, wb.datemode))).strftime('%d/%m/%Y')
                #                     dt = datetime.strptime(dt, '%d/%m/%Y')
                #                     s_date = dt

                #                     if s_date:
                #                         pur_order_qry += ',date_order'
                #                         pur_order_params += (s_date,)
                #                         pur_order_values += ", %s"



                #         pur_order_qry += ') values (' + pur_order_values + ') RETURNING id'
                #         cr.execute(pur_order_qry, pur_order_params)
                #         purchase_order_rec = cr.fetchone()
                #         supplier_id = purchase_order_rec and purchase_order_rec[0]

                # cr.commit()
        return True     