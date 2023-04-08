# -*- coding: utf-8 -*-
{
    'name': 'Partner Account Summary',
    'version': '1.1',
    'description': """Partner Account Summary""",
    'category': 'Account',
    'author': 'Ingenieria ADHOC, Tahir Aduragba',
    'website': 'www.ingadhoc.com',
    'depends': [
        'account',
        #'report_aeroo',
        ],
    'data': [
        'wizard/account_summary_wizard_view.xml',
        'report/account_summary_report.xml',
        'view/partner_account_summary.xml',],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
