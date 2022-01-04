# -*- coding: utf-8 -*-
{
    'name': "sv_membrete",

    'summary': """
       Permite agregar membretes a los reportes""",

    'description': """
        Permite agregar membretes a los reportes,
        RECUERDE QUE DEBE CAMBIARSE EL DISE;O EN LOS AJUSTES A report_membrete
        """,


    'author': "Exelity",
    'website': "https://exelitycorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sv_canal','sv_ruta'],

    # always loaded
    'data': [
        'views/views.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
