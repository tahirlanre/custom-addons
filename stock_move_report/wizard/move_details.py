# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.osv import fields, osv


class move_details(osv.osv_memory):
    _name = 'move.details'
    _columns = {
        'move_id': fields.many2one('stock.move', 'Move Name'),
        'picking_type_id': fields.many2one('stock.picking.type', 'Picking Type'),
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End', required=True),
        'type': fields.selection([('in','Inward'),('out','Outward'),('return','Returns')],string='Type',required=True),
    }
    
    
    _defaults = {
        'date_start': fields.date.context_today,
        'date_end': fields.date.context_today,
        'type': 'in',
    }

    def move_report(self, cr, uid, ids, context=None):
    
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end', 'user_ids', 'type'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'stock_move_report.report_stockmove', data=datas, context=context)
        
        