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
# TODO update description & add static/description folder

{
    'name': 'Stock Move Report',
    'version': '1.1',
    'category': 'Warehouse',
    'sequence': 6,
    'summary': '',
    'description': """
Stock Move Report (Inward & Outward)
===========================


    """,
    'author': 'Tahir Aduragba',
    'depends': ["stock",],
    'data': [
     'stock_move_report.xml',
     'wizard/move_details.xml',
     'views/report_stockmove.xml',  
        
    ],
    'demo': [
       
    ],
    'test': [
   
    ],
    'installable': True,
 
  
    'website': '',
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
