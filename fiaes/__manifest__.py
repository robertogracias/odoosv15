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
    "depends": ['stock','purchase','hr','fleet','sale_management','account_asset','survey'],
    "data": [
        'security/ir.model.access.csv'
        ,'views/fiaes.xml'
        ,'views/catalogos.xml'
        ,'views/templates.xml'
        ,'views/catalogos_d.xml'

    ],
    "installable": True,
    "application": True,
    "auto_install": False,

}
