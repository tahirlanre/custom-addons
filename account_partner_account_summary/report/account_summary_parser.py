# -*- coding: utf-8 -*-
from openerp import _
from openerp.exceptions import Warning
from openerp.report.report_sxw import rml_parse
from openerp.report import report_sxw
from openerp.osv import fields, osv
import logging
logger = logging.getLogger('report_aeroo')


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        uid = 1
        super(self.__class__, self).__init__(cr, uid, name, context)
        # Se fuerza el usuario administador por un error de permisos que no
        # pude detectar para usuarios sin permiso contable, solo con "sale
        # user"

        if not context:
            return None
        partner_ids = context.get('active_ids', False)
        if not partner_ids:
            return None
        if not isinstance(partner_ids, list):
            partner_ids = [partner_ids]

        self.localcontext.update({
            'context': context,
            'get_summary_moves_data': self.get_summary_moves_data,
            'get_summary_initial_amounts': self.get_summary_initial_amounts,
            'get_summary_final_balance': self.get_summary_final_balance,
            'initial_balance': self.initial_balance,
        })
        
    def _get_str_tuple(self, list_to_convert):
        return "(" + ",".join(["'%s'" % x for x in list_to_convert]) + ")"

    def initial_balance(self, form, context=None):
        res = self.get_summary_initial_amounts(form, context)
        if res['credit'] or res['debit']:
            return True
        return False

    def get_summary_initial_amounts(self, form, context=None):
        #self.ensure_one()
        #context = self._context
        """from_date = context.get('from_date', False)
        company_id = context.get('company_id', False)
        account_types = context.get('account_types')
        if not account_types:
            raise Warning(_('Account_types not in context!'))"""
        
        from_date = form['from_date'] #context.get('from_date', False)
        to_date = form['to_date'] #context.get('to_date', False)
        company_id = form['company_id'] #context.get('company_id', False)
        account_types = ['payable', 'receivable'] #context.get('account_types')
        
        partner_ids = context.get('active_id', False)
        
        keys = ['debit', 'credit', 'balance']
        if not from_date:
            return dict(zip(keys, [0.0, 0.0, 0.0]))
        other_filters = " AND m.date < \'%s\'" % from_date
        if company_id:
            other_filters += " AND m.company_id = %i" % company_id

        query = """SELECT SUM(l.debit), SUM(l.credit), SUM(l.debit- l.credit)
            FROM account_move_line l
            LEFT JOIN account_account a ON (l.account_id=a.id)
            LEFT JOIN account_move m ON (l.move_id=m.id)
            WHERE a.type IN %s
            AND l.partner_id = %i
            %s
              """ % (
                self._get_str_tuple(account_types), partner_ids, other_filters)
        self.cr.execute(query)
        res = self.cr.fetchall()

        return dict(zip(keys, res[0]))
    
    def get_summary_moves_data(self, form, context=None):
        #self.ensure_one()
        
        if not context:
            return None
        partner_ids = context.get('active_id', False)
        if not partner_ids:
            return None
        #if not isinstance(partner_ids, list):
        #    partner_ids = [partner_ids]

        #context = self._context
        from_date = form['from_date'] #context.get('from_date', False)
        to_date = form['to_date'] #context.get('to_date', False)
        company_id = form['company_id'] #context.get('company_id', False)
        account_types = ['payable', 'receivable'] #context.get('account_types')
        if not account_types:
            raise Warning(_('Account_types not in context!'))

        other_filters = ""
        if from_date:
            other_filters += " AND m.date >= \'%s\'" % from_date
        if to_date:
            other_filters += " AND m.date <= \'%s\'" % to_date
        if company_id:
            other_filters += " AND m.company_id = %i" % company_id
        
        query = """SELECT l.move_id, l.date_maturity, l.debit, l.credit, l.id
            FROM account_move_line l
            LEFT JOIN account_account a ON (l.account_id=a.id)
            LEFT JOIN account_move m ON (l.move_id=m.id)
            WHERE a.type IN %s
            AND l.partner_id = %i
            %s
            GROUP BY m.date, l.id, l.move_id, l.date_maturity
            ORDER BY m.date ASC, l.date_maturity DESC
              """ % (
                self._get_str_tuple(account_types), partner_ids, other_filters)
        self.cr.execute(query)
        res = self.cr.fetchall()

        lines_vals = []
        balance = self.get_summary_initial_amounts(form, context)['balance'] or 0.0
        for line in res:
            line_balance = line[2] - line[3]
            if line_balance > 0:
                debit = line_balance
                credit = 0.0
            elif line_balance < 0:
                debit = 0.0
                credit = -line_balance
            else:
                # if no line balance, then we dont print it
                continue
            balance += line_balance
            lines_vals.append({
                'move': self.pool.get('account.move').browse(self.cr, self.uid, line[0], context=context),
                'move_line': self.pool.get('account.move.line').browse(self.cr, self.uid, line[4], context=context),
                'date_maturity': line[1],
                'debit': debit,
                'credit': credit,
                'balance': balance,
            })
        return lines_vals
        
    def get_summary_final_balance(self, form, context=None):
        #self.ensure_one()
        
        #context = self._context
        from_date = form['from_date'] #context.get('from_date', False)
        to_date = form['to_date'] #context.get('to_date', False)
        company_id = form['company_id'] #context.get('company_id', False)
        account_types = ['payable', 'receivable'] #context.get('account_types')
        
        partner_ids = context.get('active_id', False)

        other_filters = ""
        if to_date:
            other_filters += " AND m.date < \'%s\'" % to_date
        if company_id:
            other_filters += " AND m.company_id = %i" % company_id

        query = """SELECT SUM(l.debit- l.credit)
            FROM account_move_line l
            LEFT JOIN account_account a ON (l.account_id=a.id)
            LEFT JOIN account_move m ON (l.move_id=m.id)
            WHERE a.type IN %s
            AND l.partner_id = %i
            %s
              """ % (
                self._get_str_tuple(account_types), partner_ids, other_filters)
        self.cr.execute(query)
        res = self.cr.fetchall()
        return res[0]
        

class report_account_summary(osv.AbstractModel):
    _name = 'report.account_partner_account_summary.partner_summary'
    _inherit = 'report.abstract_report'
    _template = 'account_partner_account_summary.partner_summary'
    _wrapped_report_class = Parser