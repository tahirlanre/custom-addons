from openerp import models, fields, api


class res_company(models.Model):
    _inherit = 'res.company' 
    
    branch = fields.Char('Branch')