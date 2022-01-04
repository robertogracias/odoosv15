# -*- coding: utf-8 -*-
{
    'name': "basculas",

    'summary': """
       Contiene funcionalidades para leer basculas por puertos com""",

    'description': """
       Contiene funcionalidades para leer basculas por puertos com
    """,

    'author': "Exelity",
    'website': "https://exelitycorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/bascula.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
