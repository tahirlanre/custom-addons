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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round

import time


class stock_product_move_report(osv.osv_memory):

    _name = "stock.product.move.report"
    _columns = {
        "date_from": fields.date("Date from", required=True),
        "date_to": fields.date("Date to", required=True),
        "product_id": fields.many2one("product.product", "Product", required=True),
        "location_id": fields.many2one(
            "stock.location",
            "Location",
            domain="[('usage', '=', 'internal')]",
            required=True,
        ),
    }
    _defaults = {
        "date_from": lambda *a: time.strftime("%Y-%m-%d"),
        "date_to": lambda *a: time.strftime("%Y-%m-%d"),
    }

    def print_report(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        datas = {"ids": context.get("active_ids", [])}
        res = self.read(
            cr,
            uid,
            ids,
            ["date_from", "product_id", "date_to", "location_id"],
            context=context,
        )
        res = res and res[0] or {}
        datas["form"] = res
        if res.get("id", False):
            datas["ids"] = [res["id"]]
        return self.pool["report"].get_action(
            cr,
            uid,
            [],
            "stock_product_move_report.move_report",
            data=datas,
            context=context,
        )
