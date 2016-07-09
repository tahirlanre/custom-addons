import logging
from openerp import models, fields, api, exceptions
from openerp.osv import osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp import netsvc, tools

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product
import time

_logger = logging.getLogger(__name__)


class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
   
    account_no = fields.Char('Account Number')
    bank_name = fields.Char('Bank Name')
    date_appoint = fields.Date('Date Appoint')
    dept = fields.Char('Department')
    gender = fields.Char('Gender')
    grade = fields.Char('Grade')
    pension_pin = fields.Char('Pension Pin')
    pfa_name = fields.Char('PFA Name')
    staff_id = fields.Char('Staff ID')
    step = fields.Char('Step')
    salary_level = fields.Many2one('hr.salary.structure', 'Salary Level')
    loan = fields.Boolean('Loan?')
    loan_amount = fields.Float('Coperative Loan Monthly Pay')
    nhf_loan = fields.Boolean('NHF Housing Loan?')
    nhf_loan_amount = fields.Float('NHF Loan Monthly Pay')

class hr_salary_structure(models.Model):
    _name = 'hr.salary.structure'

    name = fields.Char('Scale')
    wage = fields.Float('Emolument per month')