# -*- coding: utf-8 -*-
{
    'name': "sv_rrhh",

    'summary': """
       localizacion para la planilla de El Salvador""",

    'description': """
         controlador para redirigir los reportes de jasper
    """,

    'author': "Exelity",
    'website': "https://exelitycorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll','hr_payroll_account','sv_jasper'],

    # always loaded
    'data': [
        'data/data.xml',
        'views/views.xml',
        'views/financiera.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
