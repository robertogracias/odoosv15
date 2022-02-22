# -*- coding: utf-8 -*-
{
    'name': "unispice",

    'summary': """
       Permite mover lotes completos entre ubicaciones""",

    'description': """
        Permite mover lotes completos entre ubicaciones
    """,

    'author': "Exelity",
    'website': "https://exelitycorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','etiquetas','basculas'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/traslado.xml',
        'views/ingreso.xml',
        'views/transformacion.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
