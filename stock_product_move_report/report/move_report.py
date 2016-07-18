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
            'initialinventory': self._intial_qty_available,
            'stock_moves': self._stock_moves,
            'stock_qty_out': self._stock_move_out_to_print,
            'stock_qty_in': self._stock_move_in_to_print,
            'get_balance': self.get_move_accumulated_balance,
            'qty_available': self._qty_available,      
        })
        self.context = context
    
    def _stock_move_in_out(self, move):
        source_in= ["supplier", "inventory", "customer"]
        source_out= ["internal"]
        stock_in = 0
        stock_out = 0
        
        if (move.location_dest_id.usage == 'internal'):
            stock_in = move.product_uom_qty
        elif (move.location_id.usage == 'internal'):
            stock_out = move.product_uom_qty
        
        return stock_in, stock_out
    
    def _stock_moves(self, form):
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        moves = []
        move_ids = move_obj.search(self.cr, self.uid, [('date','>=',form['date_from'] + ' 00:00:00'), ('date','<=',form['date_to'] + ' 23:59:59'),('product_id', '=', form['product_id'][0]),'|',('location_dest_id.usage','=','internal'),('location_id.usage','=','internal'),('state', '=', 'done')],order="date")
        moves = move_obj.browse(self.cr, self.uid, move_ids)
        return moves
        
    def get_move_accumulated_balance(self, form, move):
        accumulated_balance = self._intial_qty_available(form)
        stock_moves = self._stock_moves(form)
        for m in stock_moves:
            accumulated_balance += self._get_stock_move_in(m) - self._get_stock_move_out(m)
            if m == move:
                break
        return accumulated_balance
               
    def _get_stock_move_out(self, move):
        return self._stock_move_in_out(move)[1]
    
    def _get_stock_move_in(self, move):
        return self._stock_move_in_out(move)[0]
    
    def _stock_move_out_to_print(self, move):
        stock_out = self._stock_move_in_out(move)[1]
        
        if stock_out == 0:
            return ''
        else:
            return stock_out
    
    def _stock_move_in_to_print(self, move):
        stock_in = self._stock_move_in_out(move)[0]
        
        if stock_in == 0:
            return ''
        else:
            return stock_in
        
    def _qty_available(self, form):
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        total_in = 0
        total_out = 0
        source_in= ["supplier", "inventory", "customer"]
        source_out= ["internal"]
        
        move_in = move_obj.search(self.cr, self.uid, [('date','<=', form['date_to'] + ' 23:59:59'),('product_id', '=', form['product_id'][0]),('location_id.usage', 'in', source_in),('location_dest_id.usage', 'not in', source_in), ('state', '=', 'done')])
        move_out = move_obj.search(self.cr, self.uid, [('date','<=', form['date_to'] + ' 23:59:59'),('product_id', '=', form['product_id'][0]),('location_id.usage', 'in', source_out), ('location_dest_id.usage', 'not in', source_out),('state', '=', 'done')])
        total_in = 0
        total_out = 0
        for m in move_obj.browse(self.cr, self.uid, move_in):
            total_in += m.product_uom_qty
        for m in move_obj.browse(self.cr, self.uid, move_out):
            total_out += m.product_uom_qty
            
        return total_in - total_out or 0
        
    def _intial_qty_available(self, form):
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        total_in = 0
        total_out = 0
        source_in= ["supplier", "inventory", "customer"]
        source_out= ["internal"]
        
        move_in = move_obj.search(self.cr, self.uid, [('date','<=', form['date_from'] + ' 00:00:00'),('product_id', '=', form['product_id'][0]),('location_id.usage', 'in', source_in),('location_dest_id.usage', 'not in', source_in), ('state', '=', 'done')])
        move_out = move_obj.search(self.cr, self.uid, [('date','<=', form['date_from'] + ' 00:00:00'),('product_id', '=', form['product_id'][0]),('location_id.usage', 'in', source_out), ('location_dest_id.usage', 'not in', source_out),('state', '=', 'done')])
        total_in = 0
        total_out = 0
        for m in move_obj.browse(self.cr, self.uid, move_in):
            total_in += m.product_uom_qty
        for m in move_obj.browse(self.cr, self.uid, move_out):
            total_out += m.product_uom_qty
            
        return total_in - total_out or 0

class report_stock_product_move_report(osv.AbstractModel):
    _name = 'report.stock_product_move_report.move_report'
    _inherit = 'report.abstract_report'
    _template = 'stock_product_move_report.move_report'
    _wrapped_report_class = Parser