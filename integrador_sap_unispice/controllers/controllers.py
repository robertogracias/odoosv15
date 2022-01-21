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

class test_unispice(http.Controller):
    
    @http.route('/territories', auth='public')
    def get_tax(self, **kw):
        return """
[
    {
        "territoryID": 18,
        "description": "Calidad"
    },
    {
        "territoryID": 9,
        "description": "CostaSur-NorOriente"
    },
    {
        "territoryID": 10,
        "description": "Delivery"
    },
    {
        "territoryID": 2,
        "description": "Guatemala"
    },
    {
        "territoryID": 27,
        "description": "Mayoreo Centro"
    },
    {
        "territoryID": 12,
        "description": "MayoreoXela"
    },
    {
        "territoryID": 22,
        "description": "MayoreoXelaII"
    },
    {
        "territoryID": 26,
        "description": "Occidente"
    },
    {
        "territoryID": 29,
        "description": "Occidente 2 (Costa)"
    },
    {
        "territoryID": 23,
        "description": "Parqueo 1 Xelaju"
    },
    {
        "territoryID": 24,
        "description": "Parqueo 2 Xelaju"
    },
    {
        "territoryID": 11,
        "description": "PDVXelaju"
    },
    {
        "territoryID": 16,
        "description": "Ruteo Antigua Guatemala"
    },
    {
        "territoryID": 20,
        "description": "Ruteo Vegetales"
    },
    {
        "territoryID": 28,
        "description": "RuteoVentasII"
    },
    {
        "territoryID": 3,
        "description": "RuteoVentasIII"
    },
    {
        "territoryID": 4,
        "description": "RuteoVentasIV"
    },
    {
        "territoryID": 13,
        "description": "RuteoVentasIX"
    },
    {
        "territoryID": 5,
        "description": "RuteoVentasV"
    },
    {
        "territoryID": 6,
        "description": "RuteoVentasVI"
    },
    {
        "territoryID": 7,
        "description": "RuteoVentasVII"
    },
    {
        "territoryID": 8,
        "description": "RuteoVentasVIII"
    },
    {
        "territoryID": 14,
        "description": "RuteoVentasX"
    },
    {
        "territoryID": 17,
        "description": "RuteoVentasXelaju2"
    },
    {
        "territoryID": 15,
        "description": "RuteoXelaju"
    },
    {
        "territoryID": 25,
        "description": "Sala de Ventas Xelaju"
    },
    {
        "territoryID": 1,
        "description": "-Sin territorio-"
    },
    {
        "territoryID": 19,
        "description": "Supermercados 2"
    },
    {
        "territoryID": 21,
        "description": "Territorio Estrategico"
    }
]

        """


    @http.route('/sales-order', auth='public')
    def get_salesorder(self, **kw):
        return """
{
        "clientCode": "", // Código de cliente/proveedor
        "clientName": "", // Nombre de cliente/proveedor
        "customerReferenceNo": "",  // Número de referencia de deudor
        "documentDate": "", // Fecha de contabilización
        "serie": 6, // Serie
        "documentNum": 1, // Número de documento
        "comments": null, // Comentarios
        "documentTotal": 0.570000, // Total (doc.)
        "shipTo": "", // Destino.
        "billTo": "", // Destinatario de factura.
        "rows": [
            {
                "itemCode": "", // Número de artículo
                "quantity": 1.000000, // Cantidad
                "price": 0.500000, // Precio por unidad
                "discountPrecentage": 0.000000, // Descuento % por linea
                "taxCode": "", // Indicador de impuestos
                "grossPrice": 0.565000, // Precio Bruto
                "warehouse": "" // Código de almacén
            }
        ]
    }

        """

    @http.route('/items', auth='public')
    def get_sucursales(self, **kw):
        return """
        [
    {
        "code": "MateriaPrima",
        "name": "My",
        "foreignName": null,
        "itemsGroup": 100,
        "uoMGroup": -1,
        "itemsPerPurchaseUnit": 1.000000,
        "quantityPerPackage": 1.000000,
        "length": null,
        "width": null,
        "height": null,
        "volume": 0.000000,
        "weight": null,
        "planingMethod": "N",
        "procurementMethod": "B",
        "orderInterval": null,
        "orderMultiple": 0.000000,
        "minimumOrderQuantity": 0.000000,
        "leadTime": null,
        "toleranceDays": null,
        "codigoOdoo": null,
        "pesoReferencia": null,
        "pesoReferenciaMinimo": null,
        "pesoReferenciaMaximo": null,
        "pesoNeto": null,
        "pesoBruto": null,
        "camaAereo": null,
        "filasAereo": null,
        "cajasPalletAereo": null,
        "camaMaritimo": null,
        "filasMaritimo": null,
        "cajasPalletMaritimo": null,
        "grupoMP": null,
        "grupoTipoMP": null,
        "grupoMPPermitida": null,
        "grupoPT": null,
        "grupoPresentacion": null,
        "grupoTipoEmpaque": null,
        "cantidadporposicion": null
    },
    {
        "code": "MEBa145x210x28mmDur",
        "name": "Bandeja blanca de duroport 145x210x28mm 2P",
        "foreignName": "Duroport 145x210x28mm 2P Tray",
        "itemsGroup": 115,
        "uoMGroup": -1,
        "itemsPerPurchaseUnit": 1.000000,
        "quantityPerPackage": 1.000000,
        "length": 0.000000,
        "width": 0.000000,
        "height": 0.000000,
        "volume": 0.000000,
        "weight": 0.000000,
        "planingMethod": "N",
        "procurementMethod": "B",
        "orderInterval": null,
        "orderMultiple": 0.000000,
        "minimumOrderQuantity": 0.000000,
        "leadTime": null,
        "toleranceDays": null,
        "codigoOdoo": null,
        "pesoReferencia": null,
        "pesoReferenciaMinimo": null,
        "pesoReferenciaMaximo": null,
        "pesoNeto": null,
        "pesoBruto": null,
        "camaAereo": null,
        "filasAereo": null,
        "cajasPalletAereo": null,
        "camaMaritimo": null,
        "filasMaritimo": null,
        "cajasPalletMaritimo": null,
        "grupoMP": null,
        "grupoTipoMP": null,
        "grupoMPPermitida": null,
        "grupoPT": null,
        "grupoPresentacion": null,
        "grupoTipoEmpaque": null,
        "cantidadporposicion": null
    },
    {
        "code": "MEBa165x215x25mmDur",
        "name": "Bandeja blanca de duroport 165x215x25mm",
        "foreignName": "165x215x25mm Duroport Tray",
        "itemsGroup": 115,
        "uoMGroup": -1,
        "itemsPerPurchaseUnit": 1.000000,
        "quantityPerPackage": 1.000000,
        "length": 0.000000,
        "width": 0.000000,
        "height": 0.000000,
        "volume": 0.000000,
        "weight": 0.000000,
        "planingMethod": "N",
        "procurementMethod": "B",
        "orderInterval": null,
        "orderMultiple": 0.000000,
        "minimumOrderQuantity": 0.000000,
        "leadTime": null,
        "toleranceDays": null,
        "codigoOdoo": null,
        "pesoReferencia": null,
        "pesoReferenciaMinimo": null,
        "pesoReferenciaMaximo": null,
        "pesoNeto": null,
        "pesoBruto": null,
        "camaAereo": null,
        "filasAereo": null,
        "cajasPalletAereo": null,
        "camaMaritimo": null,
        "filasMaritimo": null,
        "cajasPalletMaritimo": null,
        "grupoMP": null,
        "grupoTipoMP": null,
        "grupoMPPermitida": null,
        "grupoPT": null,
        "grupoPresentacion": null,
        "grupoTipoEmpaque": null,
        "cantidadporposicion": null
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
        "territory": null,
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
        ]
    }
]
       """

    @http.route('/business-partners/vendors', auth='public')
    def partners(self, **kw):
        return """
        [
    {
        "code": "MPAB00192",
        "name": "Angel Bocel Castellanos",
        "foreingName": "Angel Bocel Castellanos",
        "bpType": "Proveedor",
        "groupCode": 112,
        "currency": "##",
        "taxID": "000000000C/F",
        "phone1": "8323763",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "territory": null,
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
        ]
    },
    {
        "code": "MPAC06466",
        "name": "Adolfo Cisneros",
        "foreingName": "Adolfo Cisneros",
        "bpType": "Proveedor",
        "groupCode": 112,
        "currency": "##",
        "taxID": "000000000C/F",
        "phone1": "",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "territory": null,
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
        ]
    },
    {
        "code": "MPAC06535",
        "name": "Alejandro de la Cruz Ajualip",
        "foreingName": "Alejandro de la Cruz Ajualip",
        "bpType": "Proveedor",
        "groupCode": 112,
        "currency": "##",
        "taxID": "000000000C/F",
        "phone1": "",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "territory": null,
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
                "addressName": "Alejandro de la Cruz Ajualip",
                "street": "",
                "city": "",
                "zipCode": "",
                "state": "2",
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            },
            {
                "addressName": "Bill to",
                "street": "",
                "city": "",
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": null,
                "addressType": "BillTo"
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
        ]
    },
    {
        "code": "MPAG06305",
        "name": "Angel Benedicto Gue Mo",
        "foreingName": "Angel Benedicto Gue Mo",
        "bpType": "Proveedor",
        "groupCode": 112,
        "currency": "##",
        "taxID": "000000000C/F",
        "phone1": "",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "territory": null,
        "empresa": null,
        "almacen": null,
        "tipoProductor": null,
        "coordinadorAgricola": null,
        "paymentTermsCode": 28,
        "priceListCode": 1,
        "creditLimit": 0.000000,
        "contacts": [],
        "addresses": [
            {
                "addressName": "Angel Benedicto Gue Mo",
                "street": "San Cristobal, Alta Verapaz",
                "city": "",
                "zipCode": "",
                "state": "1",
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            },
            {
                "addressName": "Bill to",
                "street": "San Cristobal, Alta Verapaz",
                "city": "",
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": null,
                "addressType": "BillTo"
            }
        ]
    },
    {
        "code": "MPAL05629",
        "name": "Ader Eudiel López López",
        "foreingName": "Ader Eudiel López López",
        "bpType": "Proveedor",
        "groupCode": 112,
        "currency": "##",
        "taxID": "168008025120",
        "phone1": "",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "territory": null,
        "empresa": null,
        "almacen": null,
        "tipoProductor": null,
        "coordinadorAgricola": null,
        "paymentTermsCode": 20,
        "priceListCode": 1,
        "creditLimit": 0.000000,
        "contacts": [],
        "addresses": [
            {
                "addressName": "Ader Eudiel López López",
                "street": "San Pedro Sacatepequez",
                "city": "",
                "zipCode": "",
                "state": "17",
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            },
            {
                "addressName": "Bill to",
                "street": "San Pedro Sacatepequez",
                "city": "",
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": null,
                "addressType": "BillTo"
            }
        ]
    },
    {
        "code": "MPAL06528",
        "name": "Alexander Geovanni Lopez Roman",
        "foreingName": "Alexander Geovanni Lopez Roman",
        "bpType": "Proveedor",
        "groupCode": 112,
        "currency": "##",
        "taxID": "000000000C/F",
        "phone1": "",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "territory": null,
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
                "addressName": "Alexander Geovanni Lopez Roman",
                "street": "",
                "city": "Ipala, Chiquimula",
                "zipCode": "",
                "state": "4",
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            },
            {
                "addressName": "Bill to",
                "street": "",
                "city": "Ipala, Chiquimula",
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": null,
                "addressType": "BillTo"
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
        ]
    },
    {
        "code": "MPAO05514",
        "name": "Anibal del Cid Ordóñez",
        "foreingName": "Anibal del Cid Ordóñez",
        "bpType": "Proveedor",
        "groupCode": 112,
        "currency": "##",
        "taxID": "00D-4 22,321",
        "phone1": "",
        "phone2": "",
        "cellular": "",
        "email": "",
        "contactPerson": null,
        "territory": null,
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
                "addressName": "Anibal del Cid Ordóñez",
                "street": "Sanarate",
                "city": "",
                "zipCode": "",
                "state": "5",
                "country": "GT",
                "taxCode": null,
                "addressType": "ShipTo"
            },
            {
                "addressName": "Bill to",
                "street": "Sanarate",
                "city": "",
                "zipCode": null,
                "state": null,
                "country": "GT",
                "taxCode": null,
                "addressType": "BillTo"
            }
        ]
    }
]
        """
