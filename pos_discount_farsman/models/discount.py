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

import logging

from openerp import models, fields, api


class pos_config(models.Model):
    _inherit = 'pos.config' 
    
    discount_product_id = fields.Many2one('product.product', 'Discount Product 1', help='The product used for discount')
    promo_product_id = fields.Many2one('product.product', 'Promo Product 1', help='The product used for promo')
    promo_qty = fields.Float(defaults=10, string='Promo Quantity 1', help='The qty of product that qualifies for promo')
    
    discount_product_id_1 = fields.Many2one('product.product', 'Discount Product 2', help='The product used for discount')
    promo_product_id_1 = fields.Many2one('product.product', 'Promo Product 2', help='The product used for promo')
    promo_qty_1 = fields.Float(defaults=10, string='Promo Quantity 2', help='The qty of product that qualifies for promo')
    
    discount_product_id_2 = fields.Many2one('product.product', 'Discount Product 3', help='The product used for discount')
    promo_product_id_2 = fields.Many2one('product.product', 'Promo Product 3', help='The product used for promo')
    promo_qty_2 = fields.Float(defaults=10, string='Promo Quantity 3', help='The qty of product that qualifies for promo')
    
    

