# -*- coding: utf-8 -*-
from openerp import http

# class AccountFinancialReportsUsability(http.Controller):
#     @http.route('/account_financial_reports_usability/account_financial_reports_usability/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_financial_reports_usability/account_financial_reports_usability/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_financial_reports_usability.listing', {
#             'root': '/account_financial_reports_usability/account_financial_reports_usability',
#             'objects': http.request.env['account_financial_reports_usability.account_financial_reports_usability'].search([]),
#         })

#     @http.route('/account_financial_reports_usability/account_financial_reports_usability/objects/<model("account_financial_reports_usability.account_financial_reports_usability"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_financial_reports_usability.object', {
#             'object': obj
#         })