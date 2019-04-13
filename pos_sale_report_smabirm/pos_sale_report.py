# -*- encoding: utf-8 -*-
##############################################################################
#
#    POS Sale Report module for Odoo
#    Copyright (C) 2018 SITASYS ()
#    @author Tahir Aduragba <sitasyslimited@gmail.com>
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

from openerp import models, fields
from openerp import tools


class pos_sale_report(models.Model):
    _inherit = 'pos.sale.report'
    
    product_categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    
    # WARNING : this code doesn't handle uom conversion for the moment
    def _sale_order_select(self):
        select = """SELECT min(sol.id)*-1 AS id,
            so.date_order AS date,
            sol.product_id AS product_id,
            pp.product_tmpl_id AS product_tmpl_id,
            so.company_id AS company_id,
            pt.categ_id AS product_categ_id,
            'Sale Order' AS origin,
            sum(sol.product_uom_qty) AS qty
            FROM sale_order_line sol
            LEFT JOIN sale_order so ON so.id = sol.order_id
            LEFT JOIN product_product pp ON pp.id = sol.product_id
            left join product_template pt on (pt.id=pp.product_tmpl_id)
            WHERE so.state NOT IN ('draft', 'sent', 'cancel')
            GROUP BY so.date_order, sol.product_id, pp.product_tmpl_id, pt.categ_id,
            so.company_id
        """
        return select

    def _pos_order_select(self):
        select = """SELECT min(pol.id) AS id,
            po.date_order AS date,
            pol.product_id AS product_id,
            pp.product_tmpl_id AS product_tmpl_id,
            po.company_id AS company_id,
            pt.categ_id AS product_categ_id,
            'Point of Sale' AS origin,
            sum(pol.qty) AS qty
            FROM pos_order_line pol
            LEFT JOIN pos_order po ON po.id = pol.order_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            left join product_template pt on (pt.id=pp.product_tmpl_id)
            WHERE po.state IN ('paid', 'done', 'invoiced')
            GROUP BY po.date_order, pol.product_id, pp.product_tmpl_id, pt.categ_id,
            po.company_id
        """
        return select