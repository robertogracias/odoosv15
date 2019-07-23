# -*- coding: utf-8 -*-

{
    "name": "fiaes",
    "category": '',
    "summary": """
       Localizacion de ODOO  para FIAES .""",
    "description": """
	   Contiene las adaptaciones de ODOO para FIAES

    """,
    "sequence": 1,
    "author": "Strategi-k",
    "website": "http://strategi-k.com",
    "version": '12.0.0.4',
<<<<<<< HEAD
    "depends": ['stock','purchase','hr','fleet','sale_management','account_asset','survey'],
=======
    "depends": ['stock','purchase','hr','fleet','sale_management'],
>>>>>>> branch 'develop' of https://github.com/robertogracias/fiaes-dev.git
    "data": [
        'security/ir.model.access.csv'
        ,'views/fiaes.xml'
        ,'views/catalogos.xml'
<<<<<<< HEAD
        ,'views/templates.xml'
        ,'views/catalogos_d.xml'

=======
        ,'views/account_account.xml'
>>>>>>> branch 'develop' of https://github.com/robertogracias/fiaes-dev.git
    ],
    "installable": True,
    "application": True,
    "auto_install": False,

}
