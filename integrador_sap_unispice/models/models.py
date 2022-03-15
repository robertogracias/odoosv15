# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#
##############################################################################
import base64
import json
import requests
import logging
import time
from datetime import datetime
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)

class integrador_territory(models.Model):
    _name='integrador_sap_unispice.territory'
    _description='Territorio importado de SAP'
    name=fields.Char("Name")
    code=fields.Char("Codigo")

class integrador_taxcode(models.Model):
    _name='integrador_sap_unispice.tax_code'
    _description='Tax Codes'
    name=fields.Char("Name")
    code=fields.Char("Codigo")

class integrador_warehouse(models.Model):
    _name='integrador_sap_unispice.warehouse'
    _description='Ware House'
    name=fields.Char("Name")
    code=fields.Char("Codigo")


class integrador_location(models.Model):
    _inherit='stock.location'
    sap_warehouse_id = fields.Many2one('integrador_sap_unispice.warehouse', string='Almacen SAP')

class integrador_prodcut(models.Model):
    _inherit='product.template'
    foreignname=fields.Char("Descripción en ingles")
    itemsgroup=fields.Integer("itemsGroup")
    uomgroup=fields.Integer("uoMGroup")
    subgrupoventa1=fields.Char("Sub Grupo de Venta")
    itemsperpurchaseunit=fields.Float("Items por unidad de compra")
    uomembalaje=fields.Char("Unidad de Embalaje")
    quantityperpackage=fields.Float("Items por paquete")
    length=fields.Float("Slength1")
    width=fields.Float("SWidth1")
    height=fields.Float("SHeight1")
    volume=fields.Float("Volumen CC")
    uomvolumen=fields.Char("Unidad de volumen")
    weight=fields.Float("SWeight1")
    planingmethod=fields.Char("planingMethod")
    procurementmethod=fields.Char("procurementmethod")
    orderinterval=fields.Char("orderInterval")
    ordermultiple=fields.Float("orderMultiple")
    minimumorderquantity=fields.Float("Cantidad minima de orden")
    leadtime=fields.Integer("leadTime")
    tolerancedays=fields.Integer("Dias de tolerancia")
    codigosap=fields.Char("Codigo SAP")
    subgrupoventa2=fields.Char("Sub Grupo de Venta 2")
    subgrupoventa3=fields.Char("Sub Grupo de Venta 3")
    pesoreferencia=fields.Float("Peso de referencia")
    pesoreferenciaminimo=fields.Float("Peso de referencia mínimo")
    pesoreferenciamaximo=fields.Float("Peso de referencia máximo")
    pesoneto=fields.Float("Peso Neto")
    pesobruto=fields.Float("Peso Bruto")
    camaaereo=fields.Integer("Cama Aereo")
    filasaereo=fields.Integer("Filas Aereo")
    cajaspalletaereo=fields.Integer("Cajas pallet aereo")
    camamaritimo=fields.Integer("Cama maritimo")
    filasmaritimo=fields.Integer("Filas Maritimo")
    cajaspalletmaritimo=fields.Integer("Cajas pallet maritimo")
    grupomp=fields.Char("grupoMP")
    grupotipomp=fields.Char("grupoTipoMP")
    grupomppermitida=fields.Char("grupoMPPermitida")
    grupopt=fields.Char("grupoPT")
    grupopresentacion=fields.Char("grupoPresentacion")
    grupotipoempaque=fields.Char("grupoTipoEmpaque")
    cantidadporposicion=fields.Float("Cantidad por posición")
    subgrupo1=fields.Char("Sub grupo 1")
    subgrupo2=fields.Char("Sub grupo 2")
    subgrupo3=fields.Char("Sub grupo 3")
    formatoliquidacion=fields.Char("Formato de liquidacion")


    def sync_producto(self,accion='update'):
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:            
            for r in self:
                _logger.info('Integrador de Productos:'+r.default_code)
                for r in self:
                    dic={}
                    dic['code']=r.codigosap
                    dic['name']=r.name
                    dic['foreignName']=r.foreignname
                    dic['itemsGroup']=r.itemsgroup
                    dic['uoMGroup']=-1
                    dic['subGrupoVenta1']=r.subgrupoventa1
                    dic['itemsPerPurchaseUnit']=r.itemsperpurchaseunit
                    dic['uoMEmbalaje']=r.uomembalaje
                    dic['quantityPerPackage']=r.quantityperpackage
                    dic['length']=r.length
                    dic['width']=r.width
                    dic['height']=r.height
                    dic['volume']=r.volume
                    if r.uomvolumen:
                        dic['uoMVolumen']=int(r.uomvolumen)
                    dic['weight']=r.weight
                    dic['planingMethod']=r.planingmethod
                    dic['procurementMethod']=r.procurementmethod
                    dic['orderInterval']=r.orderinterval
                    dic['orderMultiple']=r.ordermultiple
                    dic['minimumOrderQuantity']=r.minimumorderquantity
                    dic['leadTime']=r.leadtime
                    dic['toleranceDays']=r.tolerancedays
                    dic['codigoOdoo']=r.default_code
                    dic['subGrupoVenta2']=r.subgrupoventa2 if r.subgrupoventa2 else ''
                    dic['subGrupoVenta3']=r.subgrupoventa3 if r.subgrupoventa3 else ''
                    dic['pesoReferencia']=r.pesoreferencia
                    dic['pesoReferenciaMinimo']=r.pesoreferenciaminimo
                    dic['pesoReferenciaMaximo']=r.pesoreferenciamaximo
                    dic['pesoNeto']=r.pesoneto
                    dic['pesoBruto']=r.pesobruto
                    dic['camaAereo']=r.camaaereo
                    dic['filasAereo']=r.filasaereo
                    dic['cajasPalletAereo']=r.cajaspalletaereo
                    dic['camaMaritimo']=r.camamaritimo
                    dic['filasMaritimo']=r.filasmaritimo
                    dic['cajasPalletMaritimo']=r.cajaspalletmaritimo
                    dic['grupoMP']=r.grupomp
                    dic['grupoTipoMP']=r.grupotipomp
                    dic['grupoMPPermitida']=r.grupomppermitida
                    dic['grupoPT']=r.grupopt
                    dic['grupoPresentacion']=r.grupopresentacion
                    dic['grupoTipoEmpaque']=r.grupotipoempaque
                    dic['cantidadporposicion']=r.cantidadporposicion
                   
                    encabezado = {"content-type": "application/json"}
                    json_datos = json.dumps(dic)
                    json_datos=json_datos.replace(': false',': null')
                    if accion=='create':
                        result = requests.post(var.valor+'/items',data = json_datos, headers=encabezado)                    
                    if accion=='update':
                        result = requests.put(var.valor+'/items',data = json_datos, headers=encabezado)
                    if accion=='deactivate':
                        result = requests.put(var.valor+'/items/deactivate/'+r.codigosap,data = json_datos, headers=encabezado)
                    if accion=='activate':
                        result = requests.put(var.valor+'/items/activate/'+r.codigosap,data = json_datos, headers=encabezado)
                    if accion=='delete':
                        result = requests.delete(var.valor+'/items/'+r.codigosap,data = json_datos, headers=encabezado)
                    

                    if result.status_code==200:
                        _logger.info('RESULTADO:'+result.text)
                    else:
                        raise ValidationError('SE HA PRODUCIDO UN ERROR'+result.text)
                        #raise ValidationError('No se pudo crear el producto en SAP: Enviado:'+json_datos+' Recibido: '+result.text)
            


class integrador_task(models.Model):
    _inherit='ir.cron'
    sap_task=fields.Boolean("Tarea de syncronizacion SAP")
    
#class integrador_category(models.Model):
#    _inherit='product.category'
#    code=fields.Integer("Codigo",select=True)

#class integrador_user(models.Model):
#    _inherit='res.users'
#    code=fields.Integer("Codigo",select=True)
#    soporte=fields.Integer("Soporte de ventas",select=True)

#class integrador_pricelist(models.Model):
#    _inherit='product.pricelist'
#    code=fields.Char("Codigo",select=True)
#    factor=fields.Float("Factor")
#    sap=fields.Char("Factor",select=True)

#class integrador_pricelistitem(models.Model):
#    _inherit='product.pricelist.item'
#    code_producto=fields.Char("Codigo producto",select=True)
#    code_cliente=fields.Char("Codigo cliente",select=True)
    
#class integrador_location(models.Model):
#    _inherit='stock.location'
#    code=fields.Char("Codigo",select=True)

class integrador_partner(models.Model):
    _inherit='res.partner'
    foreingname=fields.Char("foreingName")
    groupcode=fields.Integer("groupCode")
    phone2=fields.Char("Telefono 2")
    contactperson=fields.Char("contactPerson")
    empresa=fields.Integer("empresa")
    almacen=fields.Integer("almacen")
    tipoproductor=fields.Char("Tipo Productor")
    coordinadoragricola=fields.Char("Coordinador Agricola")
    paymenttermscode=fields.Integer("paymentTermsCode")
    pricelistcode=fields.Integer("priceListCode")
    creditlimit=fields.Float("creditLimit")
    firstname=fields.Char("first name")
    lastname=fields.Char("last name")
    territory_id=fields.Many2one(comodel_name='integrador_sap_unispice.territory', string="Territorio")
    taxcode=fields.Char("taxCode")
    sap_state=fields.Char("state")
    grupoproductor=fields.Char("Grupo Productor")
    codigocosto=fields.Char("Codigo de costo")

    bptype=fields.Char("bpType")
    currency=fields.Char("currency")

    unispice_sociedad=fields.Boolean('Sociedad UNISPICE')

class integrador_property(models.Model):
    _name='integrador_sap_unispice.property'
    _description='Atributo de una tarea de integracion'
    name=fields.Char('Atributo',select=True)
    valor=fields.Char('Valor')


    
#class integrador_ruta(models.Model):
#    _name='integrador_sap.ruta'
#    _description='Ruta'
#    codigo=fields.Char('Codigo')
#    name=fields.Char('Ruta')
    
#class integrador_taxcode(models.Model):
#    _name='integrador_sap.taxcode'
#    _description='Impuesto'
#    codigo=fields.Char('Codigo')
#    name=fields.Char('Impuesto')
#    Rate=fields.Char('Rate')
    
#class integrador_taxcode(models.Model):
#    _name='integrador_sap.gestion'
#    _description='Gestion'
#    codigo=fields.Char('Codigo')
#    name=fields.Char('Name')

#class integrador_sucursal(models.Model):
#    _name='integrador_sap.sucursal'
#    _description='Sucursal'
#    name=fields.Char('Sucursal')
#    codigo=fields.Char('Codigo')
    
#class integrador_price_item(models.Model):
#    _name='integrador_sap.item_price'
#    _description='Item de la cola de syncronizacion de precios'
#    name=fields.Char('Item')
#    #tipo de item 0:Lista de precios  1: Precio especial
#    tipo=fields.Integer("Tipo de Item")
#    item_code=fields.Char("Codigo del producto")
#    pricelist=fields.Char("Codigo de la lista de precios")
#    weightpound=fields.Float("Peso en Libras")
#    price=fields.Float("Precio")
#    client_code=fields.Char("Codigo del cliente")
#    fromdate=fields.Date("Desde")
#    todate=fields.Date("Hasta")
#    period_price=fields.Float("Precio del periodo")
#    procesado=fields.Boolean("Procesado")
    

class integrador_orderline(models.Model):
    _inherit='sale.order.line'
    taxcode=fields.Char("TAX CODE")
    grossprice=fields.Float("Gross Price")
    warehouse=fields.Char("Codigo del almacen")
    
#    @api.onchange('price_unit','product_id')
#    def set_pound_price(self):
#        for r in self:
#            if r.product_id:
#                if r.product_id.product_tmpl_id.pounds:
#                    r.pound_price=r.price_unit/r.product_id.product_tmpl_id.pounds

class integrador_order(models.Model):
    _inherit='sale.order'
    sap_order=fields.Char("Orden en SAP")
    unispice_sociedad_id = fields.Many2one('res.partner', string='Sociedad En SAP')
    sap_warehouse_id = fields.Many2one('integrador_sap_unispice.warehouse', string='Almacen SAP')
    taxcode_id = fields.Many2one('integrador_sap_unispice.tax_code', string='Taxcode')


    def sync_sap(self):
        _logger.info('Integrador de ordenes de venta')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        varserie=self.env['integrador_sap_unispice.property'].search([('name','=','sap_venta_serie')],limit=1)
        if var:
            for r in self:
                dic={}
                dic['clientCode']=r.partner_id.ref
                dic['clientName']=r.partner_id.name
                dic['customerReferenceNo']=r.partner_id.ref
                dic['documentDate']=r.date_order.strftime("%Y-%m-%d")
                dic['documentDueDate']=r.date_order.strftime("%Y-%m-%d")
                dic['series']=int(varserie.valor)
                dic['comments']=r.notes
                dic['documentDate']=0.0
                dic['billTo']=r.unispice_sociedad_id.contact_address_complete
                dic['shipTo']=r.picking_type_id.warehouse_id.partner_id.contact_address_complete
                lines=[]
                for l in r.order_line:
                    line={}
                    line['itemCode']=l.product_id.codigosap
                    line['quantity']=l.product_uom_qty
                    line['price']=l.price_unit
                    line['discountPercentage']=0
                    line['taxCode']=r.taxcode_id.code
                    line['grossPrice']=l.price_unit
                    line['warehouseCode']=r.sap_warehouse_id.code
                    lines.append(line)
                dic['rows']=lines
                encabezado = {"content-type": "application/json"}
                json_datos = json.dumps(dic)
                json_datos=json_datos.replace(': false',': null')
                result = requests.post(var.valor+'/sales-order',data = json_datos, headers=encabezado)
                _logger.info('RESULTADO:'+result.text)
                
                if result.status_code==200:
                    respuesta=json.loads(result.text)
                    _logger.info('RESULTADO:'+result.text)
                    if 'documentNum' in respuesta:
                        r.sap_order=respuesta['documentNum']
                        #for l in respuesta['rows']:
                        #    for linea in r.order_line:
                        #        if linea.product_id.codigosap==l['itemCode']:
                        #            linea.price_unit=l['unitPrice']
                    else:
                        raise ValidationError('No se pudo crear la Orden en SAP: Enviado:'+json_datos+' Recibido: '+result.text)    
                else:                        
                    raise ValidationError('No se pudo crear la Orden en SAP: Enviado:'+json_datos+' Recibido: '+result.text)
    
#    def sync_sap(self):
#        _logger.info('Integrador de ordenes')
#        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
#        if var:
#            for r in self:
#                dic={}
#                dic['clientCode']=r.partner_id.ref
#                dic['clientName']=r.partner_id.name
#                dic['documentDate']=r.date_order.strftime("%Y-%m-%d")
#                dic['documentDueDate']=r.validity_date.strftime("%Y-%m-%d")
#                dic['salesPersonCode']=r.user_id.code
#                dic['comments']=r.note
#                dic['nrc']=r.partner_id.nrc
#                dic['nit']=r.partner_id.nit
#                dic['giro']=r.partner_id.giro
#                dic['fechaDocumento']=r.date_order.strftime("%Y-%m-%d")
#                dic['razonSocial']=r.partner_id.razon_social
#                dic['direccion']=r.partner_shipping_id.street
#                dic['sucursal']=r.sucursal_id.codigo
#                dic['ruta']=r.ruta_id.codigo
#                dic['responsable']=r.ruta_id.codigo
#                dic['gestion']=r.gestion.codigo
#                lines=[]
#                for l in r.order_line:
#                    line={}
#                    line['itemCode']=l.product_id.default_code
#                    line['quantity']=l.product_uom_qty
#                    for t in l.tax_id:
#                        line['taxCode']=t.name
#                    line['price']=l.price_unit
#                    line['discountPercent']=l.discount
#                    line['salesPersonCode']=r.user_id.code
#                    line['text']=l.name
#                    lines.append(line)
#                dic['orderDetail']=lines
#                encabezado = {"content-type": "application/json"}
#                json_datos = json.dumps(dic)
#                result = requests.post(var.valor+'/sales-order',data = json_datos, headers=encabezado)
#                _logger.info('RESULTADO:'+result.text)
#                respuesta=json.loads(result.text)
#                if 'order' in respuesta:
#                    r.sap_order=respuesta['order']
#                else:
#                    raise ValidationError('No se pudo crear la orden en SAP:'+respuesta['message'])

class integrador_purchase_order_line(models.Model):
    _inherit='purchase.order.line'
    sap_warehouse_id = fields.Many2one('integrador_sap_unispice.warehouse', string='Almacen SAP')


class integrador_purchase_order(models.Model):
    _inherit='purchase.order'
    code=fields.Integer("Codigo")
    customerreferenceno=fields.Char("Número de referencia de deudor")
    serie=fields.Char("Serie")
    documentnum=fields.Char("Numero de documento")
    sap_order=fields.Char("Orden en SAP")
    taxdate=fields.Date('Fecha Impuestos')
    unispice_sociedad_id = fields.Many2one('res.partner', string='Sociedad En SAP')
    sap_warehouse_id = fields.Many2one('integrador_sap_unispice.warehouse', string='Almacen SAP')
    taxcode_id = fields.Many2one('integrador_sap_unispice.tax_code', string='Taxcode')

    
    def sync_sap(self):
        _logger.info('Integrador de ordenes de compra')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        varserie=self.env['integrador_sap_unispice.property'].search([('name','=','sap_compra_serie')],limit=1)
        if var:
            for r in self:
                dic={}
                dic['partnerCode']=r.partner_id.ref
                dic['partnerName']=r.partner_id.name
                dic['baseCurrency']=r.currency_id.name
                if r.partner_id.contactperson:
                    dic['contactPersonCode']=r.partner_id.contactperson
                dic['series']=int(varserie.valor)                  
                dic['documentDate']=r.date_order.strftime("%Y-%m-%d")
                dic['documentDueDate']=r.date_planned.strftime("%Y-%m-%d")
                dic['taxDate']=r.taxdate.strftime("%Y-%m-%d")
                dic['comments']=r.notes
                dic['billTo']=r.unispice_sociedad_id.contact_address_complete
                dic['shipTo']=r.picking_type_id.warehouse_id.partner_id.contact_address_complete
                dic['paymentTermsCode']=r.partner_id.paymenttermscode
                lines=[]
                for l in r.order_line:
                    line={}
                    line['itemCode']=l.product_id.codigosap
                    line['warehouseCode']=r.sap_warehouse_id.code
                    line['itemDescription']=l.name
                    line['quantity']=l.product_uom_qty
                    #line['unitPrice']=l.price_unit
                    #line['discountPercentage']=0
                    line['taxCode']=r.taxcode_id.code
                    lines.append(line)
                dic['rows']=lines
                encabezado = {"content-type": "application/json"}
                json_datos = json.dumps(dic)
                json_datos=json_datos.replace(': false',': null')
                result = requests.post(var.valor+'/purchase-order',data = json_datos, headers=encabezado)
                _logger.info('RESULTADO:'+result.text)
                
                if result.status_code==200:
                    respuesta=json.loads(result.text)
                    _logger.info('RESULTADO:'+result.text)
                    if 'documentNum' in respuesta:
                        r.sap_order=respuesta['documentNum']
                        for l in respuesta['rows']:
                            for linea in r.order_line:
                                if linea.product_id.codigosap==l['itemCode']:
                                    linea.price_unit=l['unitPrice']
                    else:
                        raise ValidationError('No se pudo crear la Orden en SAP: Enviado:'+json_datos+' Recibido: '+result.text)    
                else:                        
                    raise ValidationError('No se pudo crear la Orden en SAP: Enviado:'+json_datos+' Recibido: '+result.text)
            
class intregrador_sap_task(models.Model):
    _name='integrador_sap_unispice.task'
    _description='Tarea de integracion con sap'
    name=fields.Char('Tarea')


                
    
    def sync_cliente(self):
        _logger.info('Integrador de Clientes')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            mapa={'ref':'code'
                ,'name':'name'
                ,'foreingname':'foreingName'
                ,'bptype':'bpType'
                ,'groupcode':'groupCode'
                ,'currency':'currency'
                ,'vat':'taxID'
                ,'phone':'phone1'
                ,'phone2':'phone2'
                ,'mobile':'cellular'
                ,'email':'email'
                ,'contactperson':'contactPerson'
#                ,'territory':'territory'
#                ,'codigocosto':'codigoCosto'
                ,'empresa':'empresa'
                ,'almacen':'almacen'
                ,'tipoproductor':'tipoProductor'
                ,'coordinadoragricola':'coordinadorAgricola'
                ,'paymenttermscode':'paymentTermsCode'
                ,'pricelistcode':'priceListCode'
                ,'creditlimit':'creditLimit'}
            mapa_contact={'name':'name'
                ,'firstname':'firstName'
                ,'lastname':'lastName'
                ,'function':'position'
                ,'email':'email'}
            mapa_addres={'name':'addressName'
                ,'street':'street'
                ,'city':'city'
                ,'taxcode':'taxCode'
                ,'zip':'zipCode'
                ,'sap_state':'state'}
            url=var.valor+'/business-partners/customers'
            response = requests.get(url)
            resultado=json.loads(response.text)            
            for r in resultado:
                code=r['code']
                partner=self.env['res.partner'].search([('ref','=',code)])

                if partner:
                    #editando la compania
                    #partner_dic=json.dumps(partner)
                    dic={}
                    editado=False
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            if partner.__getitem__(odookey)!=r[sapkey]:
                                editado=True
                                dic[odookey]=r[sapkey]
                    territory=self.env['integrador_sap_unispice.territory'].search([('code','=',r['territory'])],limit=1)
                    if territory:
                        if  partner.territory_id and (partner.territory_id.id!=territory.id):
                            editado=True
                            dic['territory_id']=territory.id
                    if editado:
                        partner.write(dic)                    
                else:
                    dic={}
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            dic[odookey]=r[sapkey]
                    dic['company_type']='company' 
                    territory=self.env['integrador_sap_unispice.territory'].search([('code','=',r['territory'])],limit=1)
                    if territory:
                        if  partner.territory_id and (partner.territory_id.id!=territory.id):
                            editado=True
                            dic['territory_id']=territory.id                
                    partner=self.env['res.partner'].create(dic)
                #Contactos
                contactos=r['contacts']
                for c in contactos:
                    contacto=self.env['res.partner'].search([('type','=','other'),('name','=',c['name']),('parent_id','=',partner.id)],limit=1)
                    if contacto:
                        #contacto_dic=json.dumps(contacto)
                        diccontacto={}
                        editado=False
                        for odookey,sapkey in mapa_contact.items():
                            if c[sapkey]!='null':
                                if contacto.__getitem__(odookey)!=c[sapkey]:
                                    editado=True
                                    diccontacto[odookey]=c[sapkey]
                        if editado:
                            contacto.write(diccontacto)
                    else:
                        diccontacto={}
                        for odookey,sapkey in mapa_contact.items():
                            if c[sapkey]!='null':
                                diccontacto[odookey]=c[sapkey]
                        diccontacto['type']='other'
                        diccontacto['parent_id']=partner.id           
                        contacto=self.env['res.partner'].create(diccontacto)
                
                #direcciones
                direcciones=r['addresses']
                for c in direcciones:
                    direccion=self.env['res.partner'].search([('type','in',('invoice','delivery')),('name','=',c['addressName']),('parent_id','=',partner.id)],limit=1)
                    if direccion:
                        #direccion_dic=json.dumps(direccion)
                        dicdireccion={}
                        editado=False
                        for odookey,sapkey in mapa_addres.items():
                            if c[sapkey]!='null':
                                if direccion.__getitem__(odookey)!=c[sapkey]:
                                    editado=True                                    
                                    dicdireccion[odookey]=c[sapkey]
                        country=self.env['res.country'].search([('code','=',c['country'])],limit=1)
                        if country:
                            if direccion.country_id and (direccion.country_id.id!=country.id):
                                editado=True
                                dicdireccion['country_id']=country.id
                        if editado:
                            direccion.write(dicdireccion)
                    else:
                        dicdireccion={}
                        for odookey,sapkey in mapa_addres.items():
                            if c[sapkey]!='null':
                                dicdireccion[odookey]=c[sapkey]
                        if c['addressType']=='BillTo':
                            dicdireccion['type']='invoice'
                        else:
                            dicdireccion['type']='delivery'
                        country=self.env['res.country'].search([('code','=',c['country'])],limit=1)
                        if country:
                            dicdireccion['country_id']=country.id
                        dicdireccion['parent_id']=partner.id           
                        direccion=self.env['res.partner'].create(dicdireccion)

    def sync_vendors(self):
        _logger.info('Integrador de Proveedores')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            mapa={'ref':'code'
                ,'name':'name'
                ,'foreingname':'foreingName'
                ,'bptype':'bpType'
                ,'groupcode':'groupCode'
                ,'currency':'currency'
                ,'vat':'taxID'
                ,'phone':'phone1'
                ,'phone2':'phone2'
                ,'mobile':'cellular'
                ,'email':'email'
                ,'contactperson':'contactPerson'
#                ,'territory':'territory'
                ,'codigocosto':'codigoCosto'
                ,'empresa':'empresa'
                ,'almacen':'almacen'
                ,'tipoproductor':'tipoProductor'
                ,'grupoproductor':'grupoProductor'
                ,'coordinadoragricola':'coordinadorAgricola'
                ,'paymenttermscode':'paymentTermsCode'
                ,'pricelistcode':'priceListCode'
                ,'creditlimit':'creditLimit'}
            mapa_contact={'name':'name'
                ,'firstname':'firstName'
                ,'lastname':'lastName'
                ,'function':'position'
                ,'email':'email'}
            mapa_addres={'name':'addressName'
                ,'street':'street'
                ,'city':'city'
                ,'taxcode':'taxCode'
                ,'zip':'zipCode'
                ,'sap_state':'state'}            
            url=var.valor+'/business-partners/vendors'
            response = requests.get(url)
            resultado=json.loads(response.text)            
            for r in resultado:
                code=r['code']
                partner=self.env['res.partner'].search([('ref','=',code)])

                if partner:
                    #editando la compania
                    #partner_dic=json.dumps(partner)
                    dic={}
                    editado=False
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            if partner.__getitem__(odookey)!=r[sapkey]:
                                editado=True
                                dic[odookey]=r[sapkey]
                    territory=self.env['integrador_sap_unispice.territory'].search([('code','=',r['territory'])],limit=1)
                    if territory:
                        if  partner.territory_id and (partner.territory_id.id!=territory.id):
                            editado=True
                            dic['territory_id']=territory.id
                    if editado:
                        partner.write(dic)                    
                else:
                    dic={}
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            dic[odookey]=r[sapkey]
                    territory=self.env['integrador_sap_unispice.territory'].search([('code','=',r['territory'])],limit=1)
                    if territory:
                        if  partner.territory_id and (partner.territory_id.id!=territory.id):
                            editado=True
                            dic['territory_id']=territory.id
                    dic['company_type']='company'                 
                    partner=self.env['res.partner'].create(dic)
                #Contactos
                contactos=r['contacts']
                for c in contactos:
                    contacto=self.env['res.partner'].search([('type','=','other'),('name','=',c['name']),('parent_id','=',partner.id)],limit=1)
                    if contacto:
                        #contacto_dic=json.dumps(contacto)
                        diccontacto={}
                        editado=False
                        for odookey,sapkey in mapa_contact.items():
                            if c[sapkey]!='null':
                                if contacto.__getitem__(odookey)!=c[sapkey]:
                                    editado=True
                                    diccontacto[odookey]=c[sapkey]
                        if editado:
                            contacto.write(diccontacto)
                    else:
                        diccontacto={}
                        for odookey,sapkey in mapa_contact.items():
                            if c[sapkey]!='null':
                                diccontacto[odookey]=c[sapkey]
                        diccontacto['type']='other'
                        diccontacto['parent_id']=partner.id           
                        contacto=self.env['res.partner'].create(diccontacto)
                
                #direcciones
                direcciones=r['addresses']
                for c in direcciones:
                    direccion=self.env['res.partner'].search([('type','in',('invoice','delivery')),('name','=',c['addressName']),('parent_id','=',partner.id)],limit=1)
                    if direccion:
                        #direccion_dic=json.dumps(direccion)
                        dicdireccion={}
                        editado=False
                        for odookey,sapkey in mapa_addres.items():
                            if c[sapkey]!='null':
                                if direccion.__getitem__(odookey)!=c[sapkey]:
                                    editado=True                                    
                                    dicdireccion[odookey]=c[sapkey]
                        country=self.env['res.country'].search([('code','=',c['country'])],limit=1)
                        if country:
                            if direccion.country_id and direccion.country_id.id!=country.id:
                                editado=True
                                dicdireccion['country_id']=country.id
                        if editado:
                            direccion.write(dicdireccion)
                    else:
                        dicdireccion={}
                        for odookey,sapkey in mapa_addres.items():
                            if c[sapkey]!='null':
                                dicdireccion[odookey]=c[sapkey]
                        if c['addressType']=='BillTo':
                            dicdireccion['type']='invoice'
                        else:
                            dicdireccion['type']='delivery'
                        country=self.env['res.country'].search([('code','=',c['country'])],limit=1)
                        if country:
                            dicdireccion['country_id']=country.id
                        dicdireccion['parent_id']=partner.id           
                        direccion=self.env['res.partner'].create(dicdireccion)


    def sync_product(self):
        _logger.info('Integrador de producto')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/items'
            mapa={'default_code':'codigoOdoo'
                ,'name':'name'
                ,'foreignname':'foreignName'
                ,'itemsgroup':'itemsGroup'
                ,'uomgroup':'uoMGroup'
                ,'subgrupoventa1':'subGrupoVenta1'
                ,'itemsperpurchaseunit':'itemsPerPurchaseUnit'
                ,'uomembalaje':'uoMEmbalaje'
                ,'quantityperpackage':'quantityPerPackage'
                ,'length':'length'
                ,'width':'width'
                ,'height':'height'
                ,'volume':'volume'
                ,'uomvolumen':'uoMVolumen'
                ,'weight':'weight'
                ,'planingmethod':'planingMethod'
                ,'procurementmethod':'procurementMethod'
                ,'orderinterval':'orderInterval'
                ,'ordermultiple':'orderMultiple'
                ,'minimumorderquantity':'minimumOrderQuantity'
                ,'leadtime':'leadTime'
                ,'tolerancedays':'toleranceDays'
                ,'codigosap':'code'
                ,'subgrupoventa2':'subGrupoVenta2'
                ,'subgrupoventa3':'subGrupoVenta3'
                ,'pesoreferencia':'pesoReferencia'
                ,'pesoreferenciaminimo':'pesoReferenciaMinimo'
                ,'pesoreferenciamaximo':'pesoReferenciaMaximo'
                ,'pesoneto':'pesoNeto'
                ,'pesobruto':'pesoBruto'
                ,'camaaereo':'camaAereo'
                ,'filasaereo':'filasAereo'
                ,'cajaspalletaereo':'cajasPalletAereo'
                ,'camamaritimo':'camaMaritimo'
                ,'filasmaritimo':'filasMaritimo'
                ,'cajaspalletmaritimo':'cajasPalletMaritimo'
                ,'grupomp':'grupoMP'
                ,'grupotipomp':'grupoTipoMP'
                ,'grupomppermitida':'grupoMPPermitida'
                ,'grupopt':'grupoPT'
                ,'grupopresentacion':'grupoPresentacion'
                ,'grupotipoempaque':'grupoTipoEmpaque'
                ,'cantidadporposicion':'cantidadporposicion'
                }
            response = requests.get(url)
            resultado=json.loads(response.text)            
            for r in resultado:
                code=r['code']
                product=self.env['product.template'].search([('default_code','=',code)])
                if product:
                    dic={}
                    editado=False
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            if product.__getitem__(odookey)!=r[sapkey]:
                                editado=True
                                dic[odookey]=r[sapkey]
                    if editado:
                        product.write(dic)                    
                else:
                    dic={}
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            dic[odookey]=r[sapkey]
                    product=self.env['product.template'].create(dic)
            
    def sync_territory(self):
        _logger.info('Integrador de territorios')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/territories'
            mapa={'code':'territoryID'
                ,'name':'description'
                }
            response = requests.get(url)
            resultado=json.loads(response.text)            
            for r in resultado:
                code=r['territoryID']
                product=self.env['integrador_sap_unispice.territory'].search([('code','=',code)])
                if product:
                    dic={}
                    editado=False
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            if product.__getitem__(odookey)!=r[sapkey]:
                                editado=True
                                dic[odookey]=r[sapkey]
                    if editado:
                        product.write(dic)                    
                else:
                    dic={}
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            dic[odookey]=r[sapkey]
                    product=self.env['integrador_sap_unispice.territory'].create(dic)                  



    def sync_taxcode(self):
        _logger.info('Integrador de taxcodes')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/tax-codes'
            mapa={'code':'code'
                ,'name':'name'
                }
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado['taxes']:
                code=r['code']
                product=self.env['integrador_sap_unispice.tax_code'].search([('code','=',code)])
                if product:
                    dic={}
                    editado=False
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            if product.__getitem__(odookey)!=r[sapkey]:
                                editado=True
                                dic[odookey]=r[sapkey]
                    if editado:
                        product.write(dic)                    
                else:
                    dic={}
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            dic[odookey]=r[sapkey]
                    product=self.env['integrador_sap_unispice.tax_code'].create(dic)
    
   

    def sync_warehouselocal(self):
        _logger.info('Integrador de warehouse')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:            
            url=var.valor+'/warehouse/local'
            mapa={'code':'warehouseCode'
                ,'name':'warehouseName'
                }
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado['warehouses']:
                code=r['warehouseCode']
                product=self.env['integrador_sap_unispice.warehouse'].search([('code','=',code)])
                if product:
                    dic={}
                    editado=False
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            if product.__getitem__(odookey)!=r[sapkey]:
                                editado=True
                                dic[odookey]=r[sapkey]
                    if editado:
                        product.write(dic)                    
                else:
                    dic={}
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            dic[odookey]=r[sapkey]
                    product=self.env['integrador_sap_unispice.warehouse'].create(dic)


    def sync_warehouseimport(self):
        _logger.info('Integrador de warehouse')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:            
            url=var.valor+'/warehouse/import'
            mapa={'code':'warehouseCode'
                ,'name':'warehouseName'
                }
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado['warehouses']:
                code=r['warehouseCode']
                product=self.env['integrador_sap_unispice.warehouse'].search([('code','=',code)])
                if product:
                    dic={}
                    editado=False
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            if product.__getitem__(odookey)!=r[sapkey]:
                                editado=True
                                dic[odookey]=r[sapkey]
                    if editado:
                        product.write(dic)                    
                else:
                    dic={}
                    for odookey,sapkey in mapa.items():
                        if r[sapkey]!='null':
                            dic[odookey]=r[sapkey]
                    product=self.env['integrador_sap_unispice.warehouse'].create(dic)
















































    def sync_categorias(self):
        _logger.info('Integrador de Categorias')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/item-groups'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                partner=self.env['product.category'].search([('code','=',code)])
                if partner:
                    dic={}
                    dic['name']=r['name']
                    partner.write(dic)
                else:
                    dic={}
                    dic['code']=r['code']
                    dic['name']=r['name']
                    self.env['product.category'].create(dic)
    



























    def sync_vendedores(self):
        _logger.info('Integrador de Vendedores')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            user_field=self.env['integrador_sap_unispice.property'].search([('name','=','sap_user_field')],limit=1)
            user_type=self.env['integrador_sap_unispice.property'].search([('name','=','sap_user_type')],limit=1)
            url=var.valor+'/sales-employee'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                partner=self.env['res.users'].search([('code','=',code)])
                email=r['eMail']
                if not r['eMail']:
                    email=str(r['code'])+'@agrosania.com'
                if partner:
                    dic={}
                    dic['name']=r['name']
                    #dic['email']=email
                    #dic['login']=email
                    if r['soporteVentaCode']!='':
                        dic['soporte']=r['soporteVentaCode']
                    partner.write(dic)
                else:
                    dic={}
                    dic['code']=r['code']
                    dic['name']=r['name']
                    dic['email']=email
                    dic['login']=email
                    if r['soporteVentaCode']!='':
                        dic['soporte']=r['soporteVentaCode']
                    dic[user_field.valor]=user_type.valor
                    self.env['res.users'].create(dic)
    
    
    def sync_locations(self):
        _logger.info('Integrador de ubicaciones')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/warehouse'
            response = requests.get(url)
            resultado=json.loads(response.text)
            parent_location=self.env['integrador_sap_unispice.property'].search([('name','=','sap_location_parent')],limit=1)
            for r in resultado:
                code=r['warehouseCode']
                location=self.env['stock.location'].search([('code','=',code)])
                if location:
                    dic={}
                    dic['name']=r['warehouseName']
                    location.write(dic)
                else:
                    dic={}
                    dic['code']=r['warehouseCode']
                    dic['name']=r['warehouseName']
                    dic['usage']='internal'
                    dic['location_id']=int(parent_location.valor)
                    self.env['stock.location'].create(dic)


    def sync_pricelist_by_items(self):
        _logger.info('Integrador de Listas de precios por cola de items')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        lista_unica=self.env['integrador_sap_unispice.property'].search([('name','=','list_price')],limit=1)
        if var:
            _logger.info('time 1:'+str(fields.Datetime.now()))
            url=var.valor+'/pricelist'
            response = requests.get(url)
            resultado=json.loads(response.text)
            item=0
            for r in resultado:
                code=r['listNumber']
                pricelist=self.env['product.pricelist'].search([('code','=',code)])
                if pricelist:
                    dic={}
                    dic['name']=r['listName']
                    dic['sap']='Si'
                    dic['factor']=r['factor']
                    pricelist.write(dic)
                else:
                    dic={}
                    dic['code']=r['listNumber']
                    dic['name']=r['listName']
                    dic['sap']='Si'
                    dic['factor']=r['factor']
                    self.env['product.pricelist'].create(dic)
            _logger.info('time 2:'+str(fields.Datetime.now()))
            url=var.valor+'/pricelists-detail'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                item+=1
                _logger.info('time 1:'+str(item))
                dic={}
                dic['name']=r['itemCode']
                dic['tipo']=0
                dic['item_code']=r['itemCode']
                dic['pricelist']=r['priceList']
                dic['weightpound']=r['weightInPounds']
                dic['price']=r['price']
                dic['procesado']=False
                if r['price']>0:
                    self.env['integrador_sap.item_price'].create(dic)
            _logger.info('time 3:'+str(fields.Datetime.now()))
            url=var.valor+'/special-price'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                item+=1
                _logger.info('time 2:'+str(item))
                dic={}
                desde=r['fromDate'][:10]
                hasta=r['toDate'][:10]
                dic['name']=r['itemCode']
                dic['tipo']=1
                dic['item_code']=r['itemCode']
                dic['client_code']=r['clientCode']
                #dic['pricelist']=r['priceList']
                dic['fromdate']=desde
                dic['todate']=hasta
                #dic['weightpound']=r['weightInPounds']
                dic['price']=r['specialPrice']
                dic['period_price']=r['periodPrice']
                dic['procesado']=False
                now = datetime.now()
                day = now.strftime("%Y%m%d")
                if day<hasta:
                    self.env['integrador_sap.item_price'].create(dic)
    
    def proccess_pricelist_items(self):
        _logger.info('Procesando Items de Precios')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','item_price_batch')],limit=1)
        count=int(var.valor)
        lista_unica=self.env['integrador_sap_unispice.property'].search([('name','=','list_price')],limit=1)
        lst=self.env['integrador_sap.item_price'].search([('procesado','=',False)],limit=count,order="id asc")
        item=0
        time1 = time.time()
        for l in lst:
            item+=1
            if l.tipo==0:
                _logger.info('Tipo 0'+str(item))
                product=self.env['product.template'].search([('default_code','=',l.item_code)],limit=1)
                lista=self.env['product.pricelist'].search([('code','=',l.pricelist)],limit=1)
                if product and lista:
                    pricelist_item=self.env['product.pricelist.item'].search([('product_tmpl_id','=',product.id),('pricelist_id','=',lista.id)],limit=1)
                    if pricelist_item:
                        pricelist_item.write({'fixed_price':l.price})
                    else:
                        dic={}
                        dic['product_tmpl_id']=product.id
                        dic['pricelist_id']=lista.id
                        dic['applied_on']='1_product'
                        dic['compute_price']='fixed'
                        dic['code_producto']=l.item_code
                        dic['fixed_price']=l.price
                        self.env['product.pricelist.item'].create(dic)
                    if lista.code==lista_unica.valor:
                        if l.weightpound>0:
                            product.write({'pounds':l.weightpound,'list_price':l.price})
                        else:
                            product.write({'list_price':l.price})
                    else:
                        if l.weightpound>0:
                            product.write({'pounds':l.weightpound})
                        clientes=self.env['res.partner'].search([('lista_original','=',lista.code)])
                        for c in clientes:
                            pricelist_item=self.env['product.pricelist.item'].search([('product_tmpl_id','=',product.id),('pricelist_id','=',c.property_product_pricelist.id)],limit=1)
                            if pricelist_item:
                                pricelist_item.write({'fixed_price':l.price})
                            else:
                                dic={}
                                dic['product_tmpl_id']=product.id
                                dic['pricelist_id']=c.property_product_pricelist.id
                                dic['applied_on']='1_product'
                                dic['compute_price']='fixed'
                                dic['code_producto']=l.item_code
                                dic['fixed_price']=l.price
                                self.env['product.pricelist.item'].create(dic)
            if l.tipo==1:
                _logger.info('Tipo 1'+str(item))
                product=self.env['product.template'].search([('default_code','=',l.item_code)],limit=1)
                cliente=self.env['res.partner'].search([('ref','=',l.client_code)],limit=1)
                if product and cliente:
                    pricelist_item=self.env['product.pricelist.item'].search([('product_tmpl_id','=',product.id),('pricelist_id','=',cliente.property_product_pricelist.id)],limit=1)
                    if pricelist_item:
                        pricelist_item.unlink()
                    dic={}
                    dic['product_tmpl_id']=product.id
                    dic['pricelist_id']=cliente.property_product_pricelist.id
                    dic['applied_on']='1_product'
                    dic['compute_price']='fixed'
                    dic['code_producto']=l.item_code
                    dic['fixed_price']=l.price
                    if l.todate>l.fromdate:
                        dic['date_start']=l.fromdate
                        dic['date_end']=l.todate
                        dic['fixed_price']=l.period_price
                    self.env['product.pricelist.item'].create(dic)
            l.write({'procesado':True})
            time2 = time.time()
            if (time2-time1)>280:
                break

    def sync_pricelist(self):
        _logger.info('Integrador de Listas de precios')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        lista_unica=self.env['integrador_sap_unispice.property'].search([('name','=','list_price')],limit=1)
        if var:
            _logger.info('time 1:'+str(fields.Datetime.now()))
            url=var.valor+'/pricelist'
            response = requests.get(url)
            resultado=json.loads(response.text)
            #parent_location=self.env['integrador_sap_unispice.property'].search([('name','=','sap_location_parent')],limit=1)
            for r in resultado:
                code=r['listNumber']
                pricelist=self.env['product.pricelist'].search([('code','=',code)])
                if pricelist:
                    dic={}
                    dic['name']=r['listName']
                    dic['sap']='Si'
                    dic['factor']=r['factor']
                    pricelist.write(dic)
                else:
                    dic={}
                    dic['code']=r['listNumber']
                    dic['name']=r['listName']
                    dic['sap']='Si'
                    dic['factor']=r['factor']
                    self.env['product.pricelist'].create(dic)
            _logger.info('time 2:'+str(fields.Datetime.now()))
            url=var.valor+'/pricelists-detail'
            response = requests.get(url)
            resultado=json.loads(response.text)
            _logger.info('Borrando items:'+str(fields.Datetime.now()))
            self.env.cr.execute("""DELETE FROM PRODUCT_PRICELIST_ITEM where code_cliente is null""")
            productos={}
            clientes={}
            tarifas={}
            lstp=self.env['product.template'].search([])
            for pr in lstp:
                productos[pr.default_code]=pr.id
            lstt=self.env['product.pricelist'].search([])
            for tr in lstt:
                tarifas[tr.code]=tr.id
            lstc=self.env['res.partner'].search([])
            for cl in lstc:
                if cl.property_product_pricelist:
                    clientes[cl.ref]=cl.property_product_pricelist.id
            _logger.info('time 3:'+str(fields.Datetime.now()))
            for r in resultado:
                ##product=self.env['product.template'].search([('default_code','=',r['itemCode'])],limit=1)
                product=None
                tarifa=None
                if r['itemCode'] in productos:
                    product=productos[r['itemCode']]
                if str(r['priceList']) in tarifas:
                    tarifa=tarifas[str(r['priceList'])]
                if product:
                    #pricelist=self.env['product.pricelist'].search([('code','=',r['priceList'])],limit=1)
                    if tarifa:
                        dic={}
                        dic['product_tmpl_id']=product
                        dic['pricelist_id']=tarifas[str(r['priceList'])]
                        dic['applied_on']='1_product'
                        dic['compute_price']='fixed'
                        dic['code_producto']=r['itemCode']
                        if str(r['priceList'])==lista_unica.valor:
                            if r['weightInPounds']>0:
                                #product.write({'pounds':r['weightInPounds']})
                                self.env.cr.execute("""update PRODUCT_template set pounds="""+str(r['weightInPounds'])+""",list_price="""+str(r['price'])+"""  where id="""+str(product)+"""""")
                            else:
                                self.env.cr.execute("""update PRODUCT_template set list_price="""+str(r['price'])+"""  where id="""+str(product)+"""""")
                        else:
                            if r['weightInPounds']>0:
                                #product.write({'pounds':r['weightInPounds']})
                                self.env.cr.execute("""update PRODUCT_template set pounds="""+str(r['weightInPounds'])+""" where id="""+str(product)+"""""")
                        if r['price']>0:
                            dic['fixed_price']=r['price']
                        #else:
                        #    dic['fixed_price']=r['factor']*product.list_price
                        self.env['product.pricelist.item'].create(dic)


    def sync_preciosespeciales(self):
        _logger.info('Integrador de precios especiales')
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        lista_unica=self.env['integrador_sap_unispice.property'].search([('name','=','list_price')],limit=1)
        if var:
            url=var.valor+'/special-price'
            response = requests.get(url)
            resultado=json.loads(response.text)
            productos={}
            clientes={}
            tarifas={}
            lstp=self.env['product.template'].search([])
            for pr in lstp:
                productos[pr.default_code]=pr.id
            lstt=self.env['product.pricelist'].search([])
            for tr in lstt:
                tarifas[tr.code]=tr.id
            lstc=self.env['res.partner'].search([])
            for cl in lstc:
                if cl.property_product_pricelist:
                    clientes[cl.ref]=cl.property_product_pricelist.id
            x=0
            for r in resultado:
                rule=self.env['product.pricelist.item'].search([('code_producto','=',r['itemCode']),('code_cliente','=',r['clientCode'])])
                x=x+1
                _logger.info('procesing:'+str(x))
                dic={}
                desde=r['fromDate'][:10]
                hasta=r['toDate'][:10]
                desdeyear=r['fromDate'][:4]
                hastayear=r['toDate'][:4]
                if rule:
                    dic['applied_on']='1_product'
                    dic['compute_price']='fixed'
                    if hasta>desde:
                        dic['date_start']=desde
                        dic['date_end']=hasta
                        dic['fixed_price']=r['periodPrice']
                    else:
                        dic['fixed_price']=r['specialPrice']
                    rule.write(dic)
                else:
                    product=None
                    cliente=None
                    if r['itemCode'] in productos:
                        product=productos[r['itemCode']]
                    if product:
                        if r['clientCode'] in clientes:
                            cliente=clientes[r['clientCode']]
                        if cliente:
                            dic['product_tmpl_id']=product
                            dic['pricelist_id']=cliente
                            dic['applied_on']='1_product'
                            dic['compute_price']='fixed'
                            dic['code_cliente']=r['clientCode']
                            if hasta>desde:
                                dic['date_start']=desde
                                dic['date_end']=hasta
                                dic['fixed_price']=r['periodPrice']
                            else:
                                dic['fixed_price']=r['specialPrice']
                            self.env['product.pricelist.item'].create(dic)
            _logger.info('time 3:'+str(fields.Datetime.now()))

    

    def sync_stock(self):
        var=self.env['integrador_sap_unispice.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/items-stock'
            ubicaciones={}
            lst=self.env['stock.location'].search([('usage','=','internal')])
            for l in lst:
                if l.code:
                    ubicaciones[l.code]=l
            picks=self.env['stock.picking'].search([('state','not in',('done','cancel'))]).action_cancel()
            response = requests.get(url)
            resultado=json.loads(response.text)
            inventory=self.env['stock.inventory'].create({'name':'Syncronizacion:'+str(fields.Datetime.now())})
            inventory.action_start()
            for r in resultado:
                code=r['itemCode']
                product=self.env['product.product'].search([('default_code','=',code)])
                if product:
                    location=ubicaciones[r['warehouseCode']]
                    if location:
                        dic={}
                        _logger.info('Producto:'+product.name)
                        item=self.env['stock.inventory.line'].search([('product_id','=',product.id),('inventory_id','=',inventory.id)],limit=1)
                        if item:
                            dic['product_qty']=r['onHand']
                            item.write(dic)
                        else:
                            dic['product_id']=product.id
                            dic['location_id']=location.id
                            dic['inventory_id']=inventory.id
                            dic['product_qty']=r['onHand']
                            self.env['stock.inventory.line'].create(dic)
            inventory.action_validate()

