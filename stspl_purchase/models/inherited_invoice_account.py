from openerp  import fields,models,api

class account_invoice(models.Model):
    
    _inherit = 'account.invoice'

    purchase_id= fields.Many2one('purchase.order','Prchase Id')
    sales_id=fields.Many2one('sale.order','Sales Id')

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    def _prepare_invoice(self,cr,uid,order, line_ids,context=None):
        res = super(purchase_order, self)._prepare_invoice(cr,uid,order, line_ids,context=context)
        res.update({'purchase_id':order.id})
        return  res
    
    
class sale_order(models.Model):
    _inherit='sale.order'

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        res=super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context=context)
        res.update({'sales_id':order.id})
        return res