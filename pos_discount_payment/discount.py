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
from openerp import models, fields, api, exceptions
from openerp.osv import osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp import netsvc, tools

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product
import time

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    discount = fields.Boolean(string='Debt Payment Method')

    

"""
class pos_config(osv.osv):
    _inherit = 'pos.config' 
    _columns = {
        'discount_pc': fields.float('Discount Percentage', help='The discount percentage'),
        'discount_product_id': fields.many2one('product.product','Discount Product', help='The product used to model the discount'),
    }
    _defaults = {
        'discount_pc': 10,
    }
"""
