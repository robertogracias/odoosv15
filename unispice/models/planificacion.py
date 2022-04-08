# -*- coding: utf-8 -*-


from ast import Store
import base64
import json
import requests
import logging
import time
from datetime import datetime
from datetime import timedelta
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


##########################################################################################################################################################
##Configuracion
class unispice_sale_order(models.Model):
    _inherit='sale.order.line'
    cantidad_programada=fields.Float('Cantidad programada',compute='calcular_cantidades',store=True)
    cantidad_realizada=fields.Float('Cantidad realizada',compute='calcular_cantidades',store=True)
    cantidad_restante=fields.Float('Cantidad restante',compute='calcular_cantidades',store=True)
    transformacion_ids=fields.One2many(comodel_name='unispice.transformacion',inverse_name='order_line_id',string='Transformacion')
    version=fields.Integer('version')
    linea_turno_id=fields.Many2one(comodel_name='unispice.linea.turno',string='Linea a asignar')

    def asignar(self):
        for r in self:
            if r.linea_turno_id:
                r.calcular_cantidades()
                if r.cantidad_restante>0:
                    dic={}
                    dic['product_id']=r.product_id.id
                    dic['cantidad_a_producir']=r.cantidad_restante
                    dic['order_line_id']=r.id
                    dic['turno_id']=r.linea_turno_id.id
                    self.env['unispice.transformacion'].create(dic)

    @api.depends('transformacion_ids','version')
    def calcular_cantidades(self):
        for r in self:
            programada=0
            realizada=0
            for t in r.transformacion_ids:
                if t.state=='Finalizado':
                    realizada=realizada+t.cantidad_prodducida
                    programada=programada+t.cantidad_prodducida
                if t.state in ('draft','iniciado'):
                    programada=programada+t.cantidad_a_producir
            r.cantidad_programada=programada
            r.cantidad_realizada=realizada
            r.cantidad_restante=r.product_uom_qty-r.cantidad_programada

class unispice_producto_panning(models.Model):
    _inherit='product.template'
    cantidad_hora=fields.Float(string='Cantidad a producir por hora')


#Lienea de produccion
class unispice_linea(models.Model):
    _name='unispice.linea'
    _description='Linea de produccion'
    name=fields.Char("Linea de produccion")
    active=fields.Boolean("Activa")

class unispice_turno(models.Model):
    _name='unispice.turno'
    _description='Turno de produccion'
    name=fields.Char(string='name',compute='get_name')
    inicio=fields.Datetime(string='Inicio',required=True)
    fin=fields.Datetime(string='Fin',required=True)
    linea_turno_ids=fields.One2many(comodel_name='unispice.linea.turno',inverse_name='turno_id',string='Programaciones')
    state=fields.Selection(selection=[('abierto','Abierto'),('cerrado','Cerrado')],string="Estado",default='abierto')

    @api.depends('inicio','fin')
    def get_name(self):
        for r in self:
            r.name=str(r.inicio)+'-'+str(r.fin)

    def abrir(self):
        for r in self:
            if r.linea_turno_ids:
                continue;
            lineas=self.env['unispice.linea'].search([('active','=',True)])
            for l in lineas:
                dic={}
                dic['linea_id']=l.id
                dic['inicio']=r.inicio
                dic['fin']=r.fin
                dic['version']=1
                dic['turno_id']=r.id
                inicio_anterior=r.inicio+timedelta(days=-1)
                anterior=self.env['unispice.linea.turno'].search([('linea_id','=',l.id),('inicio','=',inicio_anterior)],limit=1)
                if anterior:
                    dic['empleados']=anterior.empleados
                else:
                    dic['empleados']=0
                self.env['unispice.linea.turno'].create(dic)


    def cerrar(self):
        for r in self:
            for l in r.linea_turno_ids:
                l.state='cerrado'
            r.state='cerrado'


class unispice_linea_turno(models.Model):
    _name='unispice.linea.turno'
    _description='Turno de linea de produccion'
    name=fields.Char(string='name',compute='get_name')
    inicio=fields.Datetime(string='Inicio',required=True)
    fin=fields.Datetime(string='Fin',required=True)
    empleados=fields.Integer(string='Cantidad de empleados',required=True)
    linea_id=fields.Many2one(comodel_name='unispice.linea',string='Linea de Produccion',required=True)
    turno_id=fields.Many2one(comodel_name='unispice.turno',string='Turno de Produccion',required=True)
    transformacion_ids=fields.One2many(comodel_name='unispice.transformacion',inverse_name='turno_id',string='Transformacion')
    version=fields.Integer(string='Version')
    duracion=fields.Float(string='Duracion',compute='calcular_carga')
    state=fields.Selection(selection=[('abierto','Abierto'),('cerrado','Cerrado')],string="Estado",default='abierto')

    carga=fields.Float(string='Carga estimada',compute='calcular_carga')
    horas_hombre=fields.Float(string='Horas hombre',compute='calcular_carga')
    horas_programadas=fields.Float(string='Horas programadas',compute='calcular_carga')
    #productividad=fields.Flaot(string='Productividad',compute='calcular_carga')

    @api.depends('linea_id','inicio','fin')
    def get_name(self):
        for r in self:
            r.name=r.linea_id.name+':'+str(r.inicio)+'-'+str(r.fin)+ '   CARGA:'+str(round(r.carga,2))

    @api.depends('transformacion_ids')
    def calcular_carga(self):
        for r in self:
            datediff=r.fin-r.inicio
            horas=datediff.total_seconds()/3600
            horas_hombre=r.empleados*horas
            horas_programadas=0
            for t in r.transformacion_ids:
                if t.product_id.cantidad_hora:
                    horas_orden=t.cantidad_a_producir/t.product_id.cantidad_hora
                else:
                    horas_orden=0
                horas_programadas=horas_programadas+horas_orden
            r.duracion=horas
            r.horas_hombre=horas_hombre
            r.horas_programadas=horas_programadas
            if horas_hombre>0:
                r.carga=(horas_programadas/horas_hombre)*100
            else:
                r.carga=0

