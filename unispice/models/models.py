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
    proveedor_id=fields.Many2one(comodel_name='res.partner',related='boleta_id.proveedor_id', string='Proveedor')
    tipo_productor=fields.Char(related='boleta_id.x_tipo_productor', string='Tipo Productor')
    fecha_cosecha=fields.Date(related='boleta_id.fecha_cosecha', string='Fecha de cosecha')
    grupo_mp=fields.Char(string='Grupo MP',compute='get_grupo')

    def get_grupo(self):
        for r in self:
            if r.product_id.x_grupo_mp:
                r.grupo_mp=r.product_id.x_grupo_mp
            else:
                r.grupo_mp=''






#######################################################################################################################################################
#######################################################################################################################################################
###



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




class unispice_product(models.Model):
    _inherit='product.template'
    is_canasta=fields.Boolean('Es Canasta')
    is_pallet=fields.Boolean('Es Pallet')
    tara=fields.Float('Tara')

    tipo_produccion=fields.Selection(selection=[('Materia Prima','Materia Prima'),('Producto Terminado','Producto Terminado'),('Sub Producto','Sub Producto'),('Otro','Otro')],string="Tipo(Produccion)",default='Materia Prima')


