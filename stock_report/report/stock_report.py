from openerp.report import report_sxw
from openerp.osv import osv
from openerp.report.report_sxw import rml_parse
import time
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from openerp.tools.float_utils import float_round



class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_stock_report': self._get_stock_report,
        })
        self.context = context
    
      
    def _get_stock_report(self, form):
        product_obj = self.pool.get('product.product')
        obj_precision = self.pool.get('decimal.precision')
        
        show_incoming = form['show_incoming']
        show_outgoing = form['show_outgoing']
        show_opening = form['show_opening']
        
        account_prec = obj_precision.precision_get(self.cr, self.uid, 'Account')
        price_prec = obj_precision.precision_get(self.cr, self.uid, 'Product Price')
        product_ids = product_obj.search(self.cr, self.uid, [])
        data = []
        
        products = product_obj.browse(self.cr, self.uid, product_ids)
        
        for product in products:
            
            factor = 1
            
            opening_stock = 0
            total_incoming_stock = 0
            total_outgoing_stock = 0
            closing_stock = 0
            stock_value = 0
            
            ### Opening Stock
            if show_opening:
                self.cr.execute("SELECT SUM(h.quantity) FROM stock_history h, stock_move m WHERE h.move_id=m.id AND h.product_id=%s AND h.location_id=%s AND m.date < %s GROUP BY h.product_id",
                       (product.id, form['location_id'][0], form['from_date'] + ' 00:00:00'))
                res = self.cr.fetchone()
                opening_stock_temp = res and res[0] or 0
                opening_stock_temp = opening_stock_temp * factor
                opening_stock = round(opening_stock_temp, account_prec)
            
            ### Total Incoming
            if show_incoming:
                self.cr.execute("SELECT SUM(h.quantity) \
                        FROM stock_history h, stock_move m \
                        WHERE h.move_id=m.id AND \
                        h.product_id=%s AND h.location_id=%s AND h.quantity > 0 AND \
                        m.date >= %s AND m.date <= %s \
                        GROUP BY h.product_id",
                        (product.id, form['location_id'][0], form['from_date'] + ' 00:00:00', form['to_date'] + ' 23:59:59'))
                res = self.cr.fetchone()
                total_incoming_stock_temp = res and res[0] or 0
                total_incoming_stock_temp = total_incoming_stock_temp * factor
                total_incoming_stock = round(total_incoming_stock_temp, account_prec)
            
            ### Total Outgoing
            if show_outgoing:
                self.cr.execute("SELECT SUM(h.quantity) \
                        FROM stock_history h, stock_move m \
                        WHERE h.move_id=m.id AND \
                        h.product_id=%s AND h.location_id=%s AND h.quantity < 0 AND \
                        m.date >= %s AND m.date <= %s \
                        GROUP BY h.product_id",
                        (product.id, form['location_id'][0], form['from_date'] + ' 00:00:00', form['to_date'] + ' 23:59:59'))
                res = self.cr.fetchone()
                total_outgoing_stock_temp = res and res[0] or 0
                total_outgoing_stock_temp = abs(total_outgoing_stock_temp * factor)
                total_outgoing_stock = round(total_outgoing_stock_temp, account_prec)
            
            ### Closing Stock
            this_day = time.strftime('%Y-%m-%d')
            if this_day == form['to_date']:
                self.cr.execute("SELECT SUM(qty) FROM stock_quant WHERE product_id=%s AND location_id=%s GROUP BY product_id",
                    (product.id, form['location_id'][0]))
            else:
                self.cr.execute("SELECT SUM(h.quantity) FROM stock_history h, stock_move m WHERE h.move_id=m.id AND h.product_id=%s AND h.location_id=%s AND m.date <= %s GROUP BY h.product_id",
                       (product.id, form['location_id'][0], form['to_date'] + ' 23:59:59'))
            res = self.cr.fetchone()
            closing_stock_temp = res and res[0] or 0
            closing_stock_temp = closing_stock_temp * factor
            closing_stock = round(closing_stock_temp, account_prec)
            
            stock_value = closing_stock * product.standard_price
            
            ## change qty to int based on uom rounding
            if (product.uom_id.rounding % 1) == 0:
                total_incoming_stock = int(total_incoming_stock)
                total_outgoing_stock = int(total_outgoing_stock)
                opening_stock = int(opening_stock)
                closing_stock = int(closing_stock)
            
            result={ 
                'name': product.name,
                'incoming': total_incoming_stock,
                'outgoing': total_outgoing_stock,
                'opening_stock': opening_stock,
                'closing_stock': closing_stock, #total_in - total_out,
                #'code': product.default_code,
                'stock_value': stock_value  #total_stock_value_in - total_stock_value_out
            }
            
            data.append(result)
        if(data):
            return data
        else:
            return {}
        
        

class report_stock_report(osv.AbstractModel):
    _name = 'report.stock_report.stock_report_view'
    _inherit = 'report.abstract_report'
    _template = 'stock_report.stock_report_view'
    _wrapped_report_class = Parser