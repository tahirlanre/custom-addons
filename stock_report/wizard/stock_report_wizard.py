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
    
    # TODO select to show incoming, outgoing, opening or closing stocks
    
    _columns = {
        'from_date': fields.date("Date from", required=True),
        'to_date': fields.date("Date to", required=True),
        'location_id': fields.many2one('stock.location', 'Location', domain="[('usage', '=', 'internal')]"),
    }
    _defaults = {
               'to_date': lambda *a: time.strftime('%Y-%m-%d'),
               'from_date': lambda *a: time.strftime('%Y-%m-%d'),
               'location_id': lambda *a: 12,        ## set location_id to WH/Stock
               }
    

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['from_date', 'to_date', 'location_id'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'stock_report.stock_report_view', data=datas, context=context)
    
    # TODO get id for WH/Stock
    def _get_wh_stock_id(self):
        pass