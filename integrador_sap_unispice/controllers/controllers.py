# -*- coding: utf-8 -*-
# from odoo import http
import logging
import pprint
import werkzeug
import json
import requests

from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

class test_agrosania(http.Controller):
    
    @http.route('/tax-types', auth='public')
    def get_tax(self, **kw):
        return '[{"code":"EXE","name":"Exento","rate":0},{"code":"IVA","name":"Impuesto al Valor","rate":13},{"code":"IVAIMP","name":"IVA Importaciones","rate":13},{"code":"PER","name":"Percepción 1%","rate":1},{"code":"RET13","name":"Retención 13% IVA Suj. Excl.","rate":13},{"code":"TASA0","name":"No Sujeto","rate":0}]'

    @http.route('/items', auth='public')
    def get_sucursales(self, **kw):
        return """
        [
    {
        "code": "MateriaPrima",
        "name": "My",
        "foreignName": null,
        "itemsGroup": 100,
        "uoMGroup": -1
    },
    {
        "code": "MEBa145x210x28mmDur",
        "name": "Bandeja blanca de duroport 145x210x28mm 2P",
        "foreignName": "Duroport 145x210x28mm 2P Tray",
        "itemsGroup": 115,
        "uoMGroup": -1
    },
    {
        "code": "MEBa165x215x25mmDur",
        "name": "Bandeja blanca de duroport 165x215x25mm",
        "foreignName": "165x215x25mm Duroport Tray",
        "itemsGroup": 115,
        "uoMGroup": -1
    },
    {
        "code": "MEBa175x230x30mmDur",
        "name": "Bandeja Negra Duroport 175x230x30 mm",
        "foreignName": "Bandeja Negra Duroport 175x230x30 mm",
        "itemsGroup": 115,
        "uoMGroup": -1
    },
    {
        "code": "MEBa175x235x25mmBio",
        "name": "Bandeja 175x235x25mm Biodegradable",
        "foreignName": "Biodegradable Tray 175x235x25mm",
        "itemsGroup": 115,
        "uoMGroup": -1
    },
    {
        "code": "MEBa180x235x30DurBl",
        "name": "Bandeja blanca de duroport 180x235x30mm",
        "foreignName": "Duroport 180x235x30mm White Tray",
        "itemsGroup": 115,
        "uoMGroup": -1
    }    
]   
        """
    
    
    @http.route('/business-partners/customers', auth='public')
    def partnercustomer(self, **kw):
        return """
        [
    {
        "code": "CLFD020",
        "name": "Fresh Delight UK Ltd.",
        "foreingName": "Fresh Delight UK Ltd.",
        "bpType": "Cliente",
        "groupCode": 104,
        "currency": "USD",
        "taxID": "000000000000",
        "phone1": "+44 (0) 20 8538 2785",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": "Javier Desana",
        "empresa": null,
        "almacen": null,
        "tipoProductor": null,
        "coordinadorAgricola": null,
        "paymentTermsCode": 52,
        "priceListCode": 1,
        "creditLimit": 0.000000,
        "contacts": [
            {
                "name": "Javier Desana",
                "firstName": "Javier Desana",
                "lastName": null,
                "position": "General Manager",
                "email": "jdesana@freshdelight.com"
            }
        ],
        "addresses": [
            {
                "addressName": "Bill to",
                "street": "Vista Business Centre, 50 Salisbury Road Heathrow",
                "city": "London",
                "zipCode": null,
                "state": null,
                "country": "GB",
                "taxCode": "IVA",
                "addressType": "BillTo"
            },
            {
                "addressName": "Destinatario de factura",
                "street": "Vista Business Centre, 50 Salisbury Road Heathrow",
                "city": "London",
                "zipCode": "",
                "state": "",
                "country": "GB",
                "taxCode": "IVA",
                "addressType": "ShipTo"
            },
            {
                "addressName": "Destinatario factura",
                "street": "Vista Business Centre, 50 Salisbury Road Heathrow",
                "city": "London",
                "zipCode": "",
                "state": "",
                "country": "GB",
                "taxCode": "IVA",
                "addressType": "ShipTo"
            },
            {
                "addressName": "Ship To",
                "street": "Vista Business Centre, 50 Salisbury Road Heathrow",
                "city": null,
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": "IVA",
                "addressType": "ShipTo"
            }
        ],
        "territories": null
    },
    {
        "code": "CLFV853",
        "name": "FRU-VEG MARKETING INC.",
        "foreingName": "FRU-VEG MARKETING INC.",
        "bpType": "Cliente",
        "groupCode": 105,
        "currency": "USD",
        "taxID": "000000000000",
        "phone1": "(305)5917766",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "empresa": null,
        "almacen": null,
        "tipoProductor": null,
        "coordinadorAgricola": null,
        "paymentTermsCode": 6,
        "priceListCode": 10,
        "creditLimit": 0.000000,
        "contacts": [],
        "addresses": [
            {
                "addressName": "Bill to",
                "street": "2300 N.W. 102 Ave",
                "city": "MIAMI",
                "zipCode": null,
                "state": null,
                "country": "US",
                "taxCode": "IVA",
                "addressType": "BillTo"
            },
            {
                "addressName": "FRU-VEG MARKETING INC.",
                "street": "2300 N.W. 102 Ave",
                "city": "MIAMI",
                "zipCode": "33172",
                "state": "FL",
                "country": "US",
                "taxCode": "IVA",
                "addressType": "ShipTo"
            }
        ],
        "territories": null
    }    
]"""

    @http.route('/business-partners/vendors', auth='public')
    def partners(self, **kw):
        return """
        [
    {
        "code": "MPAB00192",
        "name": "Angel Bocel Castellanos",
        "foreingName": "Angel Bocel Castellanos",
        "bpType": "Cliente",
        "groupCode": 112,
        "currency": "##",
        "taxID": "000000000C/F",
        "phone1": "8323763",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "empresa": null,
        "almacen": null,
        "tipoProductor": null,
        "coordinadorAgricola": null,
        "paymentTermsCode": 14,
        "priceListCode": 1,
        "creditLimit": 0.000000,
        "contacts": [],
        "addresses": [
            {
                "addressName": "Bill to",
                "street": "2do. Cantón Santa María de Jesús",
                "city": "Sacatepéquez",
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": null,
                "addressType": "BillTo"
            },
            {
                "addressName": "Destinatario de factura",
                "street": "2do. Cantón Santa María de Jesús",
                "city": "Sacatepéquez",
                "zipCode": "",
                "state": "",
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            },
            {
                "addressName": "Destinatario factura",
                "street": "2do. Cantón Santa María de Jesús",
                "city": "Sacatepéquez",
                "zipCode": "",
                "state": "",
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            },
            {
                "addressName": "Ship To",
                "street": "2do. Cantón Santa María de Jesús",
                "city": null,
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            }
        ],
        "territories": null
    },
    {
        "code": "MPAC06466",
        "name": "Adolfo Cisneros",
        "foreingName": "Adolfo Cisneros",
        "bpType": "Cliente",
        "groupCode": 112,
        "currency": "##",
        "taxID": "000000000C/F",
        "phone1": "",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "empresa": null,
        "almacen": null,
        "tipoProductor": null,
        "coordinadorAgricola": null,
        "paymentTermsCode": 14,
        "priceListCode": 1,
        "creditLimit": 0.000000,
        "contacts": [],
        "addresses": [
            {
                "addressName": "Adolfo Cisneros",
                "street": "",
                "city": "",
                "zipCode": "",
                "state": "7",
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            },
            {
                "addressName": "Ship To",
                "street": "Aldea Patzocom",
                "city": null,
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            }
        ],
        "territories": null
    }    
]
        """
