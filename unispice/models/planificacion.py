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


##########################################################################################################################################################
##Configuracion
class unispice_sale_order(models.Model):
    _inherit='sale.order.line'
    cantidad_programada=fields.Float('Cantidad programada',compute='calcular_cantidades',store=True)
    cantidad_realizada=fields.Float('Cantidad realizada',compute='calcular_cantidades',store=True)
    transformacion_ids=fields.One2many(comodel_name='unispice.transformacion',inverse_name='order_line_id',string='Transformacion')
    version=fields.Integer('version')

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

class unispice_producto_panning(models.Model):
    _inherit='product.template'
    cantidad_hora=fields.Float(string='Cantidad a producir por hora')


#Lienea de produccion
class unispice_linea(models.Model):
    _name='unispice.linea'
    _description='Linea de produccion'
    name=fields.Char("Linea de produccion")


class unispice_linea_turno(models.Model):
    _name='unispice.linea.turno'
    _description='Turno de linea de produccion'
    name=fields.Char(string='name',compute='get_name')
    inicio=fields.Datetime(string='Inicio')
    fin=fields.Datetime(string='Fin')
    empleados=fields.Integer(string='Cantidad de empleados')
    linea_id=fields.Many2one(comodel_name='unispice.linea',string='Linea de Produccion',related='turno_id.linea_id')
    transformacion_ids=fields.One2many(comodel_name='unispice.transformacion',inverse_name='order_line_id',string='Transformacion')

    carga=fields.Float(string='Carga estimada',compute='calcular_carga')
    #productividad=fields.Flaot(string='Productividad',compute='calcular_carga')

    def calcular_carga(self):
        for r in self:
            datediff=r.fin-r.inicio
            horas=datediff.total_seconds()/3600
            horas_hombre=r.empleado*horas
            horas_programadas=0
            for t in r.transformacion_ids:
                if t.product_id.cantidad_hora:
                    horas_orden=t.cantidad_a_producir/t.product_id.cantidad_hora
                else:
                    horas_orden=0
                horas_programadas=horas_programadas+horas_orden
            if horas_hombre>0:
                r.carga=(horas_programadas/horas_hombre)*100
            else:
                r.carga=0

