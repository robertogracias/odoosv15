# -*- coding: utf-8 -*-
{
    'name': "etiquetas",

    'summary': """
       Contiene funcionalidades producir las etiquetas asociadas a los productos""",

    'description': """
        Contiene funcionalidades producir las etiquetas asociadas a los productos
    """,

    'author': "Exelity",
    'website': "https://exelitycorp.com/",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','stock'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/etiqueta.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
