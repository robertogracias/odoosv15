# -*- coding: utf-8 -*-


from ast import Store
import base64
import json
import requests
import logging
import time
from datetime import datetime
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class unispice_company(models.Model):
    _inherit='res.company'
    internal_transfer_id=fields.Many2one(comodel_name='stock.picking.type', string='Transferencia interna')
    inbound_transfer_id=fields.Many2one(comodel_name='stock.picking.type', string='Transferencia de ingreso')
    transform_transfer_id=fields.Many2one(comodel_name='stock.picking.type', string='Transferencia de Transformacion')
    tranformacion_seq_id=fields.Many2one(comodel_name='ir.sequence', string='Numeracion')






class unispice_lote(models.Model):
    _inherit='stock.production.lot'
    canastas=fields.Integer("Canastas")
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet')
    tara_pallet=fields.Float('Tara pallet',related='pallet_id.tara',store=True)
    boleta_id=fields.Many2one(comodel_name='unispice.recepcion', string='Boleta')
    liquidado=fields.Boolean("Liquidado")







###################################################################################################################################################333
####Clases para la solicitud de materias primas
class unispice_solicitud(models.Model):
    _name='unispice.solicitud'
    _inherit='mail.thread'
    _description='Permite realizar las solicitudes materia prima'
    name=fields.Char('Solicitud de Materia Prima',default="/")
    note=fields.Char("Notas",tracking=True)
    state=fields.Selection(selection=[('draft','Borrador'),('Solicitado','Entrada'),('Cerrado','Cerrado')],string="Estado",default='draft',tracking=True)
    pallet_ids=fields.One2many(comodel_name='unispice.solicitud.pallet', string='Pallets',inverse_name='solicitud_id')
    fecha_solicitud=fields.Date("Fecha de Entrada",tracking=True)
    pallet_id=fields.Many2one(comodel_name='stock.production.lot', string='Pallet a Agregar',domain='[("liquidado","=",False)]')


    #cambia el estado a solicitado
    def solicitar(self):
        for r in self:
            r.state='Solicitado'
            r.fecha_solicitud=datetime.now()
            r.name=self.env['ir.sequence'].next_by_code('unispice.sol')
            for l in r.pallet_ids:
                l.state='Solicitado'

    #Cierra los 
    def cerrar(self):
        for r in self:
            r.state='Cerrado'
            for l in r.pallets_id:
                if l.state=='Entregado':
                    r.state='Cancelado'

    def addline(self):
        for r in self:
            if r.pallet_id:
                lote=self.env['stock.production.lot'].search([('name', '=', r.pallet_id.name)],limit=1)
                quant=None
                if lote:
                    #validando pallet
                    anterior=self.env['unispice.solicitud.pallet'].search([('lot_id','=',lote.id),('state','!=','Cancelado')],limit=1)
                    if anterior:
                        raise UserError('El pallet ya esta en otra solicitud')
                    #validando cantidades            
                    quants=self.env['stock.quant'].search([('lot_id', '=', lote.id),('available_quantity','>',0)])
                    if quants:
                        x=0
                        for q in quants:
                            if q.location_id.usage=='internal':
                                x=x+1
                        if x>1:
                            raise UserError('EL LOTE HA SIDO DIVIDIDO')
                        else:
                            if x==1:
                                quant=q
                            else:
                                raise UserError('EL LOTE NO TIENE EXISTENCIAS')
                    else:
                        raise UserError('EL LOTE NO TIENE EXISTENCIAS')
                else:
                    raise UserError('EL LOTE NO ESTA REGISTRADO')
                dic={}
                dic['lot_id']=lote.id
                dic['solicitud_id']=r.id
                dic['state']='draft'
                dic['location_src_id']=quant.location_id.id
                dic['boleta_id']=lote.boleta_id.id
                dic['canastas']=lote.canastas
                dic['peso_bruto']=quant.available_quantity+(lote.tara_canasta*lote.canastas)+lote.tara_pallet
                dic['tara_canasta']=lote.tara_canasta
                dic['tara_pallet']=lote.tara_pallet
                dic['peso_neto']=quant.available_quantity

                self.env['unispice.solicitud.pallet'].create(dic)
     


#palet solicitada
class unispice_solicitud_detail(models.Model):
    _name='unispice.solicitud.pallet'
    _description='Pallet solicitada'

    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    state=fields.Selection(selection=[('draft','Borrador'),('Solicitado','Solicitado'),('Entregado','Entregado'),('Cancelado','Cancelado')],string="Estado",default='draft')
    solicitud_id=fields.Many2one(comodel_name='unispice.solicitud', string='Solicutd')
    location_src_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion')
    ubicado=fields.Boolean("Localizado")

    #atributos que se registran al cambiar el lote
    boleta_id=fields.Many2one(comodel_name='unispice.recepcion', string='Boleta')
    product_id=fields.Many2one(comodel_name='product.product',related='lot_id.product_id' ,string='Producto')
    cantidad=fields.Float('Cantidad')
    canastas=fields.Integer("Canastas")
    peso_bruto=fields.Float("Peso bruto")
    tara_canasta=fields.Float('Tara canasta',related='lot_id.tara_canasta',store=True)
    tara_pallet=fields.Float('Tara Palet',related='lot_id.tara_pallet',store=True)
    peso_neto=fields.Float('Peso neto',store=True)

    #atributos para el movimiento
    peso_obtenido=fields.Float("Peso Obtenido")
    canastas_transferir=fields.Integer("Canastas a transferir")
    location_dest_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion de destino')
    peso_neto_transferir=fields.Float("Peso neto a transferir",compute='get_peso_neto')
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')

    @api.depends('peso_obtenido','canastas_transferir')
    def get_peso_neto(self):
        for r in self:
            r.peso_neto_transferir=r.peso_obtenido-(r.tara_canasta*r.canastas_transferir)-r.tara_pallet


    def cancelar(self):
        for r in self:
            r.state='Cancelados'


    def get_from_bascula(self):
        for r in self:
            r.bascula_id.leer()
            peso=r.bascula_id.ultima_lectura
            r.peso_obtenido=peso


    #movimientos del traslado.
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Movimiento de producto')
    ajuste_id=fields.Many2one(comodel_name='stock.inventory', string='Ajuste de Inventario')

    def entregar(self):
        for r in self:
            ##crear movimiento de producto
            
            ##Creando Ajuste
            dicA={}
            dicA['name']='Ajuste '+r.lot_id.name
            dicA['location_ids']=[(6,0,[r.location_src_id.id])]
            dicA['product_ids']=[(6,0,[r.lot_id.product_id.id,r.lot_id.canasta_id.id])]
            dicA['prefill_counted_quantity']='counted'
            ajuste=self.env['stock.inventory'].create(dicA)
            ajuste.action_start()
            
            for l in ajuste.line_ids:
                if l.prod_lot_id.id==r.lot_id.id:
                    l.product_qty=r.peso_neto_transferir
                if l.product_id.id==r.lot_id.canasta_id.id:
                    l.product_qty=l.product_qty+(r.canastas-r.canastas_transferir)
            ajuste.action_validate()
            r.ajuste_id=ajuste.id


            #creando el picking
            dic={}
            dic['picking_type_id']=r.location_dest_id.company_id.inbound_transfer_id.id
            dic['move_type']='one'
            dic['origin']='Solicitud MP'+r.solicitud_id.name
            dic['location_dest_id']=r.location_dest_id.id
            dic['location_id']=r.location_src_id.id
            pick=self.env['stock.picking'].create(dic)
            #creando la linea de producto
            dicl={}
            dicl['company_id']=r.location_dest_id.company_id.id
            dicl['date']=datetime.today()
            dicl['location_dest_id']=r.location_dest_id.id
            dicl['location_id']=r.location_src_id.id
            dicl['name']=r.lot_id.product_id.name+' '+r.lot_id.name
            dicl['origin']='Solicitud MP'+r.solicitud_id.name
            dicl['product_id']=r.lot_id.product_id.id                
            dicl['product_uom']=r.lot_id.product_id.uom_id.id
            dicl['product_uom_qty']=r.peso_neto_transferir
            dicl['picking_id']=pick.id
            self.env['stock.move'].create(dicl)
            #creando la linea de las canastas
            dicl={}
            dicl['company_id']=r.location_dest_id.company_id.id
            dicl['date']=datetime.today()
            dicl['location_dest_id']=r.location_dest_id.id
            dicl['location_id']=r.location_src_id.id
            dicl['name']='Canastas '+r.lot_id.name
            dicl['origin']='Solicitud MP'+r.solicitud_id.name
            dicl['product_id']=r.lot_id.canasta_id.id                
            dicl['product_uom']=1
            dicl['product_uom_qty']=r.canastas_transferir
            dicl['picking_id']=pick.id
            self.env['stock.move'].create(dicl)
            pick.action_confirm()
            pick.action_assign()
            for x in pick.move_line_ids_without_package:
                if x.product_id.tracking=='lot':
                    x.write({'qty_done':x.product_uom_qty,'lot_id':r.lot_id.id,'origin':'Solicitud MP'+r.solicitud_id.name})
                else:
                    x.write({'qty_done':x.product_uom_qty,'origin':'Solicitud MP'+r.solicitud_id.name})
            pick.button_validate()
            r.state='Entregado'
            r.picking_id=pick.id



    def open_form(self):
        for r in self:
            compose_form = self.env.ref('unispice.unispice_solicitud_linea_form', False)
            ctx = dict(
            )
            return {
                'name': 'Transferencia de Pallet',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'unispice.solicitud.pallet',
                'res_id': r.id,
                'views': [(compose_form.id, 'form')],
                'target': 'new',
                'view_id': 'compose_form.id',
                'flags': {'action_buttons': True},
                'context': ctx
            }

    
#######################################################################################################################################################
#######################################################################################################################################################
###

#Lienea de produccion
class unispice_linea(models.Model):
    _name='unispice.linea'
    _description='Linea de produccion'
    name=fields.Char("Linea de produccion")

#Centro de produccion se asociad se asocia a una linea de produccion  
#Tiene una ubicacion de entrada y salida
class unispice_workcenter(models.Model):
    _inherit='mrp.workcenter'
    #ubicacion de entrada
    location_input_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion de entrada')
    #ubicacion de salida de producto terminado
    location_output_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion de salida')
    #Linea de produccion asociada
    linea_id=fields.Many2one(comodel_name='unispice.linea', string='Linea de produccion')
    #tipo de proceso
    tipo=fields.Selection(selection=[('mp','Materia Prima'),('pt','Producto terminado')],string="Tipo de proceso",default='mp')



#######################################################################################################################################################
#######################################################################################################################################################
###Transformmacion 
class unispice_production_order(models.Model):
    _name='unispice.transformacion'
    _description='Ingreso a las ordenes de produccion'
    _inherit='mail.thread'
    #Nombre se genera a partir de una secuencia
    name=fields.Char('Orden de transformacion')
    #Estado de la transformacion
    state=fields.Selection(selection=[('draft','Borrador'),('Iniciado','Iniciado'),('Finalizado','Finalizaro')],string="Estado",default='draft')
    #Proceso en el que se desarrollara la transformacion
    proceso_id=fields.Many2one(comodel_name='mrp.workcenter', string='Proceso')
    #Producto terminado a producir
    product_id=fields.Many2one(comodel_name='product.product', string='Producto')
    #fecha y hora de inicio
    producto_rechazo_id=fields.Many2one(comodel_name='product.product', string='Producto de rechazo')
    #fecha y hora de inicio
    fecha_start=fields.Datetime("Fecha de Inicio")
    #fecha y hora de finalizacion
    fecha_end=fields.Datetime("Fecha de Finalizacion")    
    
    #Lotes de ingreso
    ingresos_mp_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_mp', string='Ingresos Materia Prima',inverse_name='transformacion_id')
    salidas_mp_ids=fields.One2many(comodel_name='unispice.transformacion.salida_mp', string='Salidas Materia Prima',inverse_name='transformacion_id')
    rechazo_mp_ids=fields.One2many(comodel_name='unispice.transformacion.salida_rechazo', string='Rechazos Materia Prima',inverse_name='transformacion_id')
    #Orden de produccion asociada al proceso
    production_id=fields.Many2one(comodel_name='mrp.production', string='Proceso de produccion')
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')

    

    def iniciar(self):
        for r in self:
            r.name=r.location_id.company_id.tranformacion_seq_id.next_by_id()
            for l in r.ingresos_mp_ids:
                quant=None
                quants=self.env['stock.quant'].search([('lot_id', '=', l.lot_id.id),('available_quantity','>',0)])
                if quants:
                    x=0
                    for q in quants:
                        if q.location_id.usage=='internal':
                            x=x+1
                            quant=q
                if x>1:
                    raise UserError('El Lote ha sido divido')
                dp={}
                dp['product_id']=r.product_id.id
                dp['company_id']=r.location_id.company_id.id
                dp['consumption']='flexible'
                dp['date_planned_start']=datetime.now()
                dp['location_dest_id']=r.location_id.id
                dp['location_src_id']=quant.location_id.id
                dp['picking_type_id']=r.location_id.company_id.transform_transfer_id.id
                dp['product_qty']=quant.available_quantity
                dp['product_uom_qty']=quant.product_uom_id.id
                dp['transformacion_id']=r.id
                dp['product_uom_id']=quant.product_uom_id.id
                production=self.env['mrp.production'].create(dp)
                #movimiento del producto
                dic1={}
                dic1['product_id']=quant.product_id.id
                dic1['location_id']=quant.location_id.id
                dic1['location_dest_id']=r.location_id.id
                dic1['company_id']=r.location_id.company_id.id
                dic1['date']=datetime.now()
                dic1['product_uom']=quant.product_uom_id.id
                dic1['product_uom_qty']=quant.available_quantity
                dic1['state']='confirmed'
                dic1['name']=r.name+' - '+l.lot_id.name
                dic1['raw_material_production_id']=production.id
                self.env['stock.move'].create(dic1)
                production.action_toggle_is_locked()
                for m in production.move_raw_ids:
                    dl={}
                    dl['location_id']=quant.location_id.id
                    dl['product_id']=quant.product_id.id
                    dl['product_uom_id']=quant.product_uom_id.id
                    dl['location_dest_id']=r.location_id.id
                    dl['lot_id']=quant.lot_id.id
                    dl['product_uom_qty']=quant.available_quantity
                    dl['qty_done']=quant.available_quantity
                    dl['move_id']=m.id
                    self.env['stock.move.line'].create(dl)
                production.action_assign()
                #for m in production.move_raw_ids:
                #    if m.reserved_availability==0:
                #        raise UserError('El Material no esta disponible')
                production.action_confirm()
                #production.button_mark_done()

                ####Creacion del pickin de las canastas
                dic={}
                dic['picking_type_id']=r.location_id.company_id.transform_transfer_id.id
                dic['move_type']='one'
                dic['origin']=r.name
                dic['location_dest_id']=r.location_id.id
                dic['location_id']=quant.location_id.id
                dic['transformacion_id']=r.id
                pick=self.env['stock.picking'].create(dic)                
                #creando la linea de las canastas
                dicl={}
                dicl['company_id']=r.location_id.company_id.id
                dicl['date']=datetime.today()
                dicl['location_dest_id']=r.location_id.id
                dicl['location_id']=r.location_id.company_id.inbound_transfer_id.default_location_src_id.id
                dicl['name']='Canastas'+l.lot_id.name
                dicl['origin']=r.name
                dicl['product_id']=l.lot_id.canasta_id.id                
                dicl['product_uom']=1
                dicl['product_uom_qty']=l.canastas
                dicl['picking_id']=pick.id
                
                pick.action_confirm()
                #pick.action_assign()
                for x in pick.move_line_ids_without_package:
                    if x.product_id.tracking=='lot':
                        x.write({'qty_done':x.product_uom_qty,'lot_id':lote.id,'origin':r.name})
                    else:
                        x.write({'qty_done':x.product_uom_qty,'origin':r.name})
                #pick.button_validate()



#################################################################################################################################################
#Linea de ingreso de materia prima
class unispice_production_line_ingreso(models.Model):
    _name='unispice.transformacion.ingreso_mp'
    _description='Ingreso a las ordenes de produccion'
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',related='lot_id.product_id',store=True)
    tara_canasta=fields.Float('Tara canasta',related='lot_id.tara_canasta',store=True)
    tara_pallet=fields.Float('Tara Palet',related='lot_id.tara_pallet',store=True)
    ##Datos de ingreso
    canastas_in=fields.Integer('Canastas',compute='get_pesos',store=True)
    peso_bruto_in=fields.Float('Peso Bruto',compute='get_pesos')
    peso_neto_in=fields.Float('Peso neto',compute='get_pesos')
    ##Datos de salida
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    canastas_out=fields.Integer('Canastas de salida')
    peso_bruto_out=fields.Float('Peso de retorno')
    peso_neto_out=fields.Float('Peso neto',compute='get_pesos_salida')
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')

    #picking de las canastas
    picking_canasta_in_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_out_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')

    @api.onchange('lot_id')
    def get_pesos(self):
        for r in self:
            r.canastas_in=r.lot_id.canastas
            r.peso_neto_in=r.lot_id.product_qty
            r.peso_bruto_in=r.lot_id.product_qty+(r.lot_id.canastas*r.tara_canasta)+r.tara_pallet


#################################################################################################################################################
#Linea de salida de materia prima
class unispice_production_line_ingreso(models.Model):
    _name='unispice.transformacion.salida_mp'
    _description='salida a las ordenes de produccion'
    #El lote se generara
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',store=True)
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    tara_pallet=fields.Float('Tara Palet',related='pallet_id.tara',store=True)
    
    ##Datos de salida
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    canastas_out=fields.Integer('Canastas de salida')
    peso_bruto_out=fields.Float('Peso de retorno')
    peso_neto_in=fields.Float('Peso neto',compute='get_pesos_salida')
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')

    #picking de las canastas
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')


#################################################################################################################################################
#Linea de salida de materia prima
class unispice_production_line_ingreso(models.Model):
    _name='unispice.transformacion.salida_rechazo'
    _description='salida a las ordenes de produccion'
    #El lote se generara
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',store=True)
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    tara_pallet=fields.Float('Tara Palet',related='pallet_id.tara',store=True)
    
    ##Datos de salida
    canastas_out=fields.Integer('Canastas de salida')
    peso_bruto_out=fields.Float('Peso de retorno')
    peso_neto_in=fields.Float('Peso neto',compute='get_pesos_salida')
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')

    #picking de las canastas
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')



##########################################################################################################################################################
##Traslado entre plantas

class unispice_traslado(models.Model):
    _name='unispice.traslado'
    _inherit='mail.thread'
    _description='Traslado entre plantas'
    _sql_constraints = [
        ('Boleta_Unico', 'unique (name)', 'El Numero de boleta debe ser unico')
    ]
    name=fields.Char('Boleta',copy=False)
    fecha_ingreso=fields.Datetime("Fecha y hora de ingreso")
    proveedor_id=fields.Many2one(comodel_name='res.partner', string='Proveedor')
    producto_id=fields.Many2one(comodel_name='product.product', string='Producto')
    etapa=fields.Char('Etapa')
    viaje_id=fields.Char('Id del viaje')
    peso_campo=fields.Float('Peso campo')
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    tara_pallet=fields.Float('Tara pallet',related='pallet_id.tara',store=True)
    notas=fields.Text("Notas")

    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    detalle_ids=fields.One2many(comodel_name='unispice.traslado.line',inverse_name='traslado_id',string='Pallets')
    state=fields.Selection(selection=[('draft','Borrador'),('done','Confirmado'),('cancel','Cancelado')],string="Estado",default='draft')
    location_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion de llegada')
    label_id=fields.Many2one(comodel_name='etiquetas.label', string='Etiqueta')    

class unispice_tralsado_line(models.Model):
    _name='unispice.traslado.line'
    _description='Linea de recepcion'
    name=fields.Char('Codigo Pallet')
    traslado_id=fields.Many2one(comodel_name='unispice.traslado', string='Boleta')
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Transferencia')
    temperatura=fields.Float("Temperatura")
    canastas=fields.Integer("Canastas")
    peso_bruto=fields.Float("Peso bruto")
    tara_canasta=fields.Float('Tara canasta',related='traslado_id.tara_canasta',store=True)
    tara_pallet=fields.Float('Tara Palet',related='traslado_id.tara_pallet',store=True)
    peso_neto=fields.Float('Peso neto',compute='get_peso_neto',store=True)
    etiqueta_id=fields.Many2one(comodel_name='etiquetas.run.item', string='Etiqueta')

    @api.depends('traslado_id','tara_canasta','peso_bruto','tara_pallet','canastas')
    def get_peso_neto(self):
        for r in self:
            r.peso_neto=r.peso_bruto-(r.canastas*r.tara_canasta)-r.tara_pallet    




##########################################################################################################################################################
##Configuracion
class unispice_tipoproducto(models.Model):
    _name='unispice.tipo_producto'
    _description='Tipo de Producto'
    name=fields.Char('Tipo de Producto')
    


class unispice_configuration(models.Model):
    _name='unispice.configuration'
    _description='Configuracion de almacenes'
    name=fields.Char('Nombre')
    partner_id=fields.Many2one(comodel_name='res.partner', string='Sociedad',domain='[("unispice_sociedad","=",True)]')
    almacen_id=fields.Many2one(comodel_name='integrador_sap_unispice.warehouse', string='Almacen')
    taxcode_id=fields.Many2one(comodel_name='integrador_sap_unispice.tax_code', string='Tax Code')



class unispice_qualitycheck(models.Model):
    _name='unispice.quatily_item'
    _description='Item del control de calidad'
    name=fields.Char('Punto a revisar')

   


class unispice_product(models.Model):
    _inherit='product.template'
    is_canasta=fields.Boolean('Es Canasta')
    is_pallet=fields.Boolean('Es Pallet')
    tara=fields.Float('Tara')

    tipo_produccion=fields.Selection(selection=[('Materia Prima','Materia Prima'),('Producto Terminado','Producto Terminado'),('Sub Producto','Sub Producto'),('Otro','Otro')],string="Tipo(Produccion)",default='Materia Prima')


class unispice_check_item(models.Model):
    _name='unispice.quatily_check_item'
    _description='Item del control de calidad'
    name=fields.Char('Punto a revisar')
    aprobado=fields.Boolean("Aprobado")
    check_id=fields.Many2one(comodel_name='quality.check', string='Control')
    muestra_afectada=fields.Float("Muestra afectada")



class unispice_product(models.Model):
    _inherit='quality.check'
    quality_ids=fields.One2many(comodel_name='unispice.quatily_check_item',inverse_name='check_id',string='Items de Calidad')
    muestra=fields.Float("Peso en lbs. de la muestra")


    @api.onchange('product_id')
    def change_product(self):
        for r in self:
            r.quality_ids.unlink()
            if r.product_id.x_grupo_mp:
                lst=self.env['unispice.quatily_item'].search([('x_grupo_mp','=',r.product_id.x_grupo_mp)])
                for p in lst:
                    dic={}
                    dic['name']=p.name
                    dic['aprobado']=False
                    dic['check_id']=r.id
                    self.env['unispice.quatily_check_item'].create(dic)
