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


