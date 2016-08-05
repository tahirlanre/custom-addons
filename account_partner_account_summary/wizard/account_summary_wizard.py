from openerp import models
from openerp.osv import osv, fields
import time



class account_summary_wizard(osv.osv_memory):
    _name = 'account_summary_wizard'
    _description = 'Partner Account Summary Wizard'

    _columns ={
        'from_date' : fields.date('From'),
        'to_date' : fields.date('To'),
        'company_id' : fields.many2one(
            'res.company',
            help="If blank are to list all movements for which the user has permission , if a company is defined will be shown only movements that company"),
        'show_invoice_detail' : fields.boolean('Show Invoice Detail'),
        'show_receipt_detail' : fields.boolean('Show Receipt Detail'),
        'result_selection' : fields.selection(
            [('customer', 'Receivable Accounts'),
             ('supplier', 'Payable Accounts'),
             ('customer_supplier', 'Receivable and Payable Accounts')],
            "Account Type's", required=True, default='customer_supplier'),

    }

    _defaults = {
               'from_date': lambda *a: time.strftime('%Y-01-01'),
               'to_date': lambda *a: time.strftime('%Y-%m-%d'),
               }

    #@api.multi
    def account_summary(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['from_date', 'to_date', 'company_id', 'show_invoice_detail', 'show_receipt_detail', 'result_selection'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'account_partner_account_summary.partner_summary', data=datas, context=context)

        """active_id = self._context.get('active_id', False)
        active_ids = self._context.get('active_ids', False)
        if not active_ids:
            active_ids = [self.env.user.partner_id]
        if not active_id:
            partner = self.env.user.partner_id
            active_id = partner.id
        else:
            partner = self.env['res.partner'].browse(active_id)
        return self.env['report'].with_context(
            from_date=self.from_date,
            to_date=self.to_date,
            company_id=self.company_id.id,
            active_id=active_id,
            active_ids=active_ids,
            show_invoice_detail=self.show_invoice_detail,
            show_receipt_detail=self.show_receipt_detail,
            result_selection=self.result_selection).get_action(
            partner.commercial_partner_id, 'account_partner_account_summary.partner_summary')"""
