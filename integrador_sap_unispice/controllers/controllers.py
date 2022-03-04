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

    @http.route('/tax-codes', auth='public')
    def get_tax(self, **kw):
        return """
{
  "taxes": [
    {
      "code": "IVA_0",
      "name": "IVA tasa cero"
    },
    {
      "code": "IVACCF",
      "name": "IVA contribuyentes"
    },
    {
      "code": "IVACOM",
      "name": "IVA Compras"
    },
    {
      "code": "IVAEXE",
      "name": "Exento de IVA"
    },
    {
      "code": "IVAEXP",
      "name": "IVA exportación"
    },
    {
      "code": "IVAFCF",
      "name": "IVA consumidor final"
    },
    {
      "code": "IVAIMP",
      "name": "IVA importación 13%"
    },
    {
      "code": "IVAIMP0",
      "name": "IVA importación tasa cero"
    },
    {
      "code": "IVAINT",
      "name": "IVA internación"
    },
    {
      "code": "IVAPER",
      "name": "IVA Percepción 1%"
    },
    {
      "code": "IVARET",
      "name": "IVA Retencion 1%"
    },
    {
      "code": "IVASUE",
      "name": "IVA sujeto excluído"
    },
    {
      "code": "IVATIC",
      "name": "IVA ticket"
    }
  ]
}

        """


    @http.route('/warehouse/local', auth='public')
    def get_warehouselocal(self, **kw):
        return """
{
  "warehouses": [
    {
      "warehouseCode": "BGRAL",
      "warehouseName": "Bodega general"
    }
  ]
}
        """
    @http.route('/warehouse/import', auth='public')
    def get_warehouseimport(self, **kw):
        return """
{
  "warehouses": [
    {
      "warehouseCode": "BODAVANT",
      "warehouseName": "Avante"
    }
  ]
}
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
    "code": "MEBa145x210x28mmDur",
    "name": "Bandeja blanca de duroport 145x210x28mm 2P",
    "foreignName": "Duroport 145x210x28mm 2P Tray",
    "itemsGroup": 115,
    "uoMGroup": -1,
    "subGrupoVenta1": null,
    "itemsPerPurchaseUnit": 1.000000,
    "uoMEmbalaje": null,
    "quantityPerPackage": 1.000000,
    "length": 0.000000,
    "width": 0.000000,
    "height": 0.000000,
    "volume": 0.000000,
    "uoMVolumen": 4,
    "weight": 0.000000,
    "planingMethod": "N",
    "procurementMethod": "B",
    "orderInterval": null,
    "orderMultiple": 0.000000,
    "minimumOrderQuantity": 0.000000,
    "leadTime": null,
    "toleranceDays": null,
    "codigoOdoo": "MEBa145x210x28mmDur",
    "subGrupoVenta2": null,
    "subGrupoVenta3": null,
    "pesoReferencia": 0.000000,
    "pesoReferenciaMinimo": 0.000000,
    "pesoReferenciaMaximo": 0.000000,
    "pesoNeto": 0.000000,
    "pesoBruto": 0.000000,
    "camaAereo": 0.000000,
    "filasAereo": 0.000000,
    "cajasPalletAereo": 0.000000,
    "camaMaritimo": 0.000000,
    "filasMaritimo": 0.000000,
    "cajasPalletMaritimo": 0.000000,
    "grupoMP": null,
    "grupoTipoMP": null,
    "grupoMPPermitida": null,
    "grupoPT": null,
    "grupoPresentacion": null,
    "grupoTipoEmpaque": "Bandeja",
    "cantidadporposicion": 0.000000
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
                "city": "London",
                "zipCode": null,
                "state": null,
                "country": "GB",
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
    "code": "MPAA06300",
    "name": "Ana Victoria Arrivillaga Farfan",
    "foreingName": "Ana Victoria Arrivillaga Farfan",
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
    "codigoCosto": null,
    "empresa": null,
    "almacen": null,
    "tipoProductor": "Productor",
    "grupoProductor": "OCCIDENTE",
    "coordinadorAgricola": "Jose Gonzalez",
    "paymentTermsCode": 28,
    "priceListCode": 1,
    "creditLimit": 0,
    "contacts": [],
    "addresses": [
      {
        "addressName": "Ana Victoria Arrivillaga Farfan",
        "street": "Santa Maria de Jesus, Sacatepequez",
        "city": "",
        "zipCode": "",
        "state": "16",
        "country": "GT",
        "taxCode": null,
        "addressType": "ShipTo"
      },
      {
        "addressName": "Bill to",
        "street": "Santa Maria de Jesus, Sacatepequez",
        "city": "",
        "zipCode": null,
        "state": null,
        "country": "GT",
        "taxCode": null,
        "addressType": "BillTo"
      }
    ]
  }]
        """
