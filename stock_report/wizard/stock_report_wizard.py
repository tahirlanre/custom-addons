# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import api, fields, models


class stock_report_wizard(models.TransientModel):
    _name = 'stock.report.wizard'
    
    from_date = fields.Date('From')
    to_date = fields.Date('To')
    location_id =fields.Many2one('stock.location', string='Location')
   
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_report.stock_report_view')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        #print 'i got here'
        return report_obj.render('stock_report.stock_report_view', docargs)