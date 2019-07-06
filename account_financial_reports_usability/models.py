# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class account_financial_reports_usability(models.Model):
#     _name = 'account_financial_reports_usability.account_financial_reports_usability'

#     name = fields.Char()

import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _

class account_common_report(osv.osv_memory):
    _inherit = "account.common.report"
    
    
    _defaults = {
            'fiscalyear_id': False,
    }