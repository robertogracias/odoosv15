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
    "depends": ['stock','purchase','hr'],
    "data": [
        'security/ir.model.access.csv'
        ,'views/catalogos.xml'
        ,'views/account_account.xml'
        ,'views/project_project.xml'
    ],
    "installable": True,
    "application": True,
    "auto_install": False,

}
