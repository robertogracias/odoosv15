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




#######################################################################################################################################################
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
    state=fields.Selection(selection=[('draft','Borrador'),('Iniciado','Iniciado'),('Finalizado','Finalizado')],string="Estado",default='draft')
    tipo=fields.Selection(selection=[('mp','Materia Prima'),('pt','Producto Terminado')],string="Tipo",default='mp')
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
    ingresos_me_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_me', string='Ingresos Material de Empaque',inverse_name='transformacion_id')
    ingresos_pt_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_pt', string='Ingresos Producto Terminado',inverse_name='transformacion_id')

    salidas_mp_ids=fields.One2many(comodel_name='unispice.transformacion.salida_mp', string='Salidas Materia Prima',inverse_name='transformacion_id')
    salidas_pt_ids=fields.One2many(comodel_name='unispice.transformacion.salida_pt', string='Salidas Materia Prima',inverse_name='transformacion_id')


    track_ids=fields.One2many(comodel_name='unispice.transformacion.time_track', string='Tomas de tiempo',inverse_name='transformacion_id')


    rechazo_mp_ids=fields.One2many(comodel_name='unispice.transformacion.salida_rechazo', string='Rechazos Materia Prima',inverse_name='transformacion_id')
    #Orden de produccion asociada al proceso
    production_id=fields.Many2one(comodel_name='mrp.production', string='Proceso de produccion')
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')

    #wharehouse
    almancen_id=fields.Many2one(comodel_name='stock.warehouse',string='Almacen Id')

    razon_pausa_id=fields.Many2one(comodel_name='unispice.transformacion.time_of',string='Razon de Pausa')
    track_id=fields.Many2one(comodel_name='unispice.transformacion.time_track',string='Traza actual')

    

    #enlaces con planificacion
    cantidad_a_producir=fields.Float(string='Cantidad a producir')
    cantidad_prodducida=fields.Float(string='Cantidad producida')
    order_line_id=fields.Many2one(comodel_name='sale.order.line',string='Orden line Id')
    turno_id=fields.Many2one(comodel_name='unispice.linea.turno',string='Turno en el que esta asignado')
    order_id=fields.Many2one(comodel_name='sale.order',string='Orden Id',related='order_line_id.order_id')
    linea_id=fields.Many2one(comodel_name='unispice.linea',string='Linea de Produccion',related='turno_id.linea_id')
    turno_state=fields.Selection(selection=[('abierto','Abierto'),('cerrado','Cerrado')],string="Estado",related='turno_id.state',store=True,default='abierto')
    partner_id=fields.Many2one(comodel_name='res.partner',string='Cliente',related='order_line_id.order_partner_id')



    def  iniciar(self):
        for r in self:
            if not r.track_id:
                dic={}
                dic['inicio']=datetime.now()
                dic['transformacion_id']=r.id
                track=self.env['unispice.transformacion.time_track'].create(dic)
                r.track_id=track.id
    
    def detener(self):
        for r in self:
            if r.track_id:
                r.track_id.write({'fin':datetime.now()})
            if not r.razon_pausa_id:
                raise UserError('Debe esepcificarse una razon')
            dic={}
            dic['inicio']=datetime.now()
            dic['transformacion_id']=r.id
            dic['time_of_id']=r.razon_pausa_id.id
            track=self.env['unispice.transformacion.time_track'].create(dic)
            r.track_id=track.id
    
    def finalizar(self):
        for r in self:
            if r.track_id:
                r.track_id.write({'fin':datetime.now()})
                



    @api.model
    def create(self, vals):
        vals['name']=self.env['ir.sequence'].next_by_code('unispice.transformacion')
        res = super(unispice_production_order, self).create(vals)
        return res
    

   


#################################################################################################################################################
#Linea de ingreso de material de empaque
class unispice_production_line_ingreso_me(models.Model):
    _name='unispice.transformacion.ingreso_me'
    _description='Ingreso a las ordenes de produccion'    
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    name=fields.Char(string='Ingreso MP',related='lot_id.name')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',related='lot_id.product_id',store=True)
    ##Datos de ingreso
    cantidad=fields.Float(string='Cantidad ')
    cantidad_out=fields.Float(string='Saldo ')
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    def get_name(self):
        for r in self:
            r.name=r.lot_id.name+' - '+r.lot_id.product_id.name



  

#Linea de ingreso de materia prima
class unispice_production_line_ingreso_mp(models.Model):
    _name='unispice.transformacion.ingreso_mp'
    _description='Ingreso a las ordenes de produccion'    
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    name=fields.Char(string='Ingreso MP',compute='get_name')
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
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    #picking de las canastas
    picking_canasta_in_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_out_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')

    def get_name(self):
        for r in self:
            r.name=r.lot_id.name+' - '+r.lot_id.product_id.name


    @api.onchange('lot_id')
    def get_pesos(self):
        for r in self:
            r.canastas_in=r.lot_id.canastas
            r.peso_neto_in=r.lot_id.product_qty
            r.peso_bruto_in=r.lot_id.product_qty+(r.lot_id.canastas*r.tara_canasta)+r.tara_pallet


    #Linea de ingreso de materia prima
class unispice_production_line_ingreso(models.Model):
    _name='unispice.transformacion.ingreso_pt'
    _description='Ingreso a las ordenes de produccion'    
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    name=fields.Char(string='Ingreso MP',compute='get_name')
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
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    #picking de las canastas
    picking_canasta_in_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_out_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')

    def get_name(self):
        for r in self:
            r.name=r.lot_id.name+' - '+r.lot_id.product_id.name

    @api.onchange('lot_id')
    def get_pesos(self):
        for r in self:
            r.canastas_in=r.lot_id.canastas
            r.peso_neto_in=r.lot_id.product_qty
            r.peso_bruto_in=r.lot_id.product_qty+(r.lot_id.canastas*r.tara_canasta)+r.tara_pallet


#################################################################################################################################################
#Linea de salida de materia prima
class unispice_production_line_salida_mp(models.Model):
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
    peso_neto_out=fields.Float('Peso neto',compute='get_pesos_salida')
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')

    #picking de las canastas
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')




class unispice_production_line_salida_pt(models.Model):
    _name='unispice.transformacion.salida_pt'
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
class unispice_production_line_rechazo(models.Model):
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


class unispice_production_time_off(models.Model):
    _name='unispice.transformacion.time_of'
    _description='Razones de tiempo muerto'
    name="razon de tiempo muerto"


class unispice_production_time_track(models.Model):
    _name='unispice.transformacion.time_track'
    _description='Toma de tiempo'
    name=fields.Char(string='Nombre')
    inicio=fields.Datetime(string='Inicio')
    fin=fields.Datetime(string='Fin')
    duracion=fields.Float(string='Duracion',compute='get_duracion')
    time_of_id=fields.Many2one(comodel_name='unispice.transformacion.time_of', string='Tiempo fuera')
    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')
    turno_id=fields.Many2one(comodel_name='unispice.linea.turno',string='Turno en el que esta asignado',related='transformacion_id.turno_id')
    linea_id=linea_id=fields.Many2one(comodel_name='unispice.linea',string='Linea de Produccion',related='transformacion_id.linea_id')

    @api.depends('inicio','fin')
    def get_duracion(self):
        for r in self:
            if r.inicio and r.fin:
                datediff=r.fin-r.inicio
                r.duracion=datediff.total_seconds()/3600
            else:
                r.duracion=0.0
