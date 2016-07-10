import time
from openerp.osv import osv
from openerp.report import report_sxw

class move_details(report_sxw.rml_parse):
    
    def _get_balance(self):
        test = "Tahir"
        return test
        
    def _get_move_type(self, form):
        type = form['type']
        
        if(type =="in"):
            return "Inward"
        elif(type=="out"):
            return "Outward"
        elif(type=="return"):
            return "Returns"
        
        return ""
    
    def _get_inventory_value(self, move):
        cost = 0.0
        product_template_object = self.pool.get('product.template')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        product_template = move.product_id.product_tmpl_id.id
        cost = product_template_object.get_history_price(self.cr, self.uid, product_template, company_id, move.date)
        if cost:
            return cost * move.product_uom_qty
        return 0
    
    def _qty_available(self, form):
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        total_in = 0
        total_out = 0
        qty_available = 0
        data = []
        source_in= ["supplier", "inventory", "customer"]
        source_out= ["internal"]
        
        ids = product_obj.search(self.cr, self.uid, [])
        
        for product in product_obj.browse(self.cr, self.uid, ids):
            move_in = move_obj.search(self.cr, self.uid, [('date','<=', form['date_end'] + ' 23:59:59'),('product_id', '=', product.id),('location_id.usage', 'in', source_in),('location_dest_id.usage', 'not in', source_in), ('state', '=', 'done')])
            move_out = move_obj.search(self.cr, self.uid, [('date','<=', form['date_end'] + ' 23:59:59'),('product_id', '=', product.id),('location_id.usage', 'in', source_out), ('location_dest_id.usage', 'not in', source_out),('state', '=', 'done')])
            total_in = 0
            total_out = 0
            for m in move_obj.browse(self.cr, self.uid, move_in):
                total_in += m.product_uom_qty
            for m in move_obj.browse(self.cr, self.uid, move_out):
                total_out += m.product_uom_qty
            result={ 
                'name': product.name,
                'qty_available': total_in - total_out
            }
            
            data.append(result)
        if(data):
            return data
        else:
            return {}
            
    def _move_details(self, form):
            
        mov_obj = self.pool.get('stock.move')
        data = []
        result = {}
        type = form['type']
        
        if(type =="in"):
            source = ["supplier", "inventory"]
        elif(type=="out"):
            source = ["internal"]
        elif(type=="return"):
            source = ["customer"]
        
        move_ids = mov_obj.search(self.cr, self.uid, [('date','>=',form['date_start'] + ' 00:00:00'), ('date','<=',form['date_end'] + ' 23:59:59'), ('location_id.usage', 'in', source), ('location_dest_id.usage', 'not in', source), ('state', '=', 'done')])
        for move in mov_obj.browse(self.cr, self.uid, move_ids):
            result = {
                'move_date': move.date,
                'product_id': move.product_id.name,
                'dest_id': move.location_dest_id.name,
                'qty': move.product_uom_qty,
                'inventory_value': self._get_inventory_value(move),
                'partner': move.picking_id.partner_id.name,
                'origin' : move.picking_id.origin
            }
            
            data.append(result)
        if data:
            return data
        else:
            return {}
        
    def __init__(self, cr, uid, name, context):
        super(move_details, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'time': time,
            'getbalance': self._get_balance,
            'move_details': self._move_details,
            'move_type': self._get_move_type,
            'qty_available': self._qty_available,
            
        })


class report_move_details(osv.AbstractModel):
    _name = 'report.stock_move_report.report_stockmove'
    _inherit = 'report.abstract_report'
    _template = 'stock_move_report.report_stockmove'
    _wrapped_report_class = move_details
