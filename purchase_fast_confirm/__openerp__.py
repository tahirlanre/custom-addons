# -*- encoding: utf-8 -*-
##############################################################################
#    
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


{
    'name': 'Purchase Fast Confirm',
    'version': '1.0',
    'category': 'Purchase',
    'summary': 'Auto confirm invoice',
    'description': """
	After confirming purchase order, automatically creates invoice, validates it.
    
    
    
    # TODO Add credits
	""",
    'author': 'Tahir Aduragba',
    'website': '',
    'depends': [   
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        #'views/purchase_view.xml',
        #'data/',        

    ],
    'demo': [
    ],
    'test': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
