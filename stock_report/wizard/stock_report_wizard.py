# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round

import time

class stock_report_wizard(osv.osv_memory):
    _name = 'stock.report'
        
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['from_date', 'to_date', 'location_id', 'show_incoming', 'show_outgoing', 'show_opening'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'stock_report.stock_report_view', data=datas, context=context)
    
    def _get_wh_stock_id(self, cr, uid, context=None):
        stock_loc_obj = self.pool.get('stock.location')
        loc_name = 'Stock'
        loc_ids = stock_loc_obj.search(cr, uid,[('name','=',loc_name),('usage','=','internal')],context=context)
        for loc in stock_loc_obj.browse(cr, uid, loc_ids):
            wh_stock_id = loc.id
        return wh_stock_id
        
    _columns = {
        'from_date': fields.date("Date from", required=True),
        'to_date': fields.date("Date to", required=True),
        'location_id': fields.many2one('stock.location', 'Location', domain="[('usage', '=', 'internal')]"),
        'show_incoming': fields.boolean('Incoming'),
        'show_outgoing': fields.boolean('Outgoing'),
        'show_opening': fields.boolean('Opening')
    }
    
    _defaults = {
               'to_date': lambda *a: time.strftime('%Y-%m-%d'),
               'from_date': lambda *a: time.strftime('%Y-%m-%d'),
               'location_id': _get_wh_stock_id,        ## set location_id to WH/Stock
               'show_incoming': False,
               'show_outgoing': False,
               'show_opening': False,
    }