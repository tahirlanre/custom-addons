import logging
logger = logging.getLogger('report_aeroo')

from openerp.report import report_sxw
from openerp.osv import osv
from openerp.report.report_sxw import rml_parse
import random
import time
import re
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from openerp.tools.float_utils import float_round
from openerp import models, fields

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'lines':self.get_lines,
            'qty_available': self._qty_available,
        })
        self.context = context     
    
    
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
            move_in = move_obj.search(self.cr, self.uid, [('date','<=', form['date_to'] + ' 23:59:59'),('product_id', '=', product.id),('location_id.usage', 'in', source_in),('location_dest_id.usage', 'not in', source_in), ('state', '=', 'done')])
            move_out = move_obj.search(self.cr, self.uid, [('date','<=', form['date_to'] + ' 23:59:59'),('product_id', '=', product.id),('location_id.usage', 'in', source_out), ('location_dest_id.usage', 'not in', source_out),('state', '=', 'done')])
            total_in = 0
            total_stock_value_in = 0
            total_out = 0
            total_stock_value_out = 0
            for m in move_obj.browse(self.cr, self.uid, move_in):
                total_in += m.product_uom_qty
                total_stock_value_in += self._get_cost_price(m)
            for m in move_obj.browse(self.cr, self.uid, move_out):
                total_out += m.product_uom_qty
                total_stock_value_out += self._get_cost_price(m)
            result={ 
                'name': product.name,
                'qty_available': total_in - total_out,
                'code': product.default_code,
                'inventory_value': total_stock_value_in - total_stock_value_out
            }
            
            data.append(result)
        if(data):
            return data
        else:
            return {}
    
    
    def _get_inventory_value(self, move):
        cost = 0.0
        user_obj = self.pool.get('res.users')
        product_template_object = self.pool.get('product.template')
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        product_template = move.product_id.product_tmpl_id.id
        cost = product_template_object.get_history_price(self.cr, self.uid, product_template, company_id, move.date)
        if cost:
            return cost * move.product_uom_qty
        return 0

    def _get_cost_price(self, move):
        cost = 0.0
        user_obj = self.pool.get('res.users')
        product_template_object = self.pool.get('product.template')
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        product_template = move.product_id.product_tmpl_id.id
        cost = move.product_id.product_tmpl_id.standard_price
        if cost:
            return cost * move.product_uom_qty
        return 0

    def get_lines(self, o):
        cr = self.cr
        uid = self.uid      
        result = []
        list_product = []
        date_start = o['date_from']
        date_end = o['date_to']
        location_outsource = o['location_id'][0]
        sql_dk = '''SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_dk
                FROM  (SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) < '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code

                UNION ALL

                SELECT sm.product_id,pt.name , pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out

                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <'%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_in'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code) table_dk GROUP BY product_id,name ,code
                    ''' % (date_start, location_outsource,location_outsource, date_start, location_outsource,location_outsource)

        sql_in_tk = '''
            SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS qty_in_tk
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) >= '%s'
                AND date_trunc('day',sm.date) <= '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code
        '''% (date_start, date_end, location_outsource,location_outsource)

        sql_out_tk = '''
            SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS qty_out_tk
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) >= '%s'
                AND date_trunc('day',sm.date) <= '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code
        '''% (date_start, date_end, location_outsource,location_outsource)

        sql_ck = '''SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_ck
                FROM  (SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <= '%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id <> %s
                AND sm.location_dest_id = %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code

                UNION ALL

                SELECT sm.product_id,pt.name , pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out

                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE date_trunc('day',sm.date) <='%s'
                AND sm.state = 'done'
                --AND sp.location_type = 'outsource_in'
                AND sm.location_id = %s
                AND sm.location_dest_id <> %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code) table_ck GROUP BY product_id,name ,code
                    ''' % (date_end, location_outsource,location_outsource, date_end, location_outsource,location_outsource)

        sql = '''
            SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS num ,
                    table_ck.product_id, table_ck.name, table_ck.code,
                    COALESCE(sum(qty_dk),0) as qty_dk,
                    COALESCE(sum(qty_in_tk),0) as qty_in_tk,
                    COALESCE(sum(qty_out_tk),0) as qty_out_tk,
                    COALESCE(sum(qty_ck),0)  as qty_ck
            FROM  (%s) table_ck
                LEFT JOIN (%s) table_in_tk on table_ck.product_id = table_in_tk.product_id
                LEFT JOIN (%s) table_out_tk on table_ck.product_id = table_out_tk.product_id
                LEFT JOIN (%s) table_dk on table_ck.product_id = table_dk.product_id
                GROUP BY table_ck.product_id, table_ck.name, table_ck.code
        ''' %(sql_ck,sql_in_tk, sql_out_tk, sql_dk)
        self.cr.execute(sql)
        data = self.cr.dictfetchall()
        for i in data:
            list_product.append({   'num': i['num'],
                                    'name': i['name'],
                                    'code': i['code'],
                                    'qty_dk': i['qty_dk'],
                                    'qty_in_tk': i['qty_in_tk'],
                                    'qty_out_tk': i['qty_out_tk'],
                                    'qty_ck': i['qty_ck'],
                                 })
        return list_product



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_history_prices = fields.One2many(
        'product.price.history', 'product_template_id',
        string='Product Price History')

        
class report_inventory_report(osv.AbstractModel):
    _name = 'report.inventory_report.inventory_report'
    _inherit = 'report.abstract_report'
    _template = 'inventory_report.inventory_report'
    _wrapped_report_class = Parser
    
