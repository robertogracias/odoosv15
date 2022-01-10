# -*- coding: utf-8 -*-
{
    'name': "hmt_suplantation",

    'summary': """
       Permite ejecutar la suplantacion de usuario en odoo utilizada por HMT""",

    'description': """
        Permite que un usuario puede indentificarse mediante un pin   para los pagos, ventas sean registrados a traves de otro usuario
    """,

    'author': "Exelity",
    'website': "https://exelitycorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sv_accounting','sv_caja','sv_invoice_so'],

    # always loaded
    'data': [
        'views/vendedores.xml',
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
