from openerp.report import report_sxw
from openerp.osv import osv
from openerp.report.report_sxw import rml_parse
import time
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from openerp.tools.float_utils import float_round



class Parser(report_sxw.rml_parse):
    def test(self):
        print 'Hello World!'

class report_stock_report(osv.AbstractModel):
    _name = 'report.stock_report.stock_report_view'
    _inherit = 'report.abstract_report'
    _template = 'stock_report.stock_report_view'
    _wrapped_report_class = Parser