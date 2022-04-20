# -*- coding: utf-8 -*-

from ast import Store
import base64
import json
import requests
import logging
import time

from datetime import datetime
from collections import OrderedDict

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class unispice_packing(models.Model):
    _name = 'unispice.packing'
    _description = 'Embalaje Producto terminado'
    lote_pallet = Float(string = 'Lote Pallet')

    # Totales a calcular
    sum_cantidad = fields.Float(string = 'Suma cantidad', compute = '_get_sum_cantidad')
    sum_peso_total = fields.Float(string = 'Suma peso total', compute = '_get_sum_peso_total')


class unispice_packing_line(models.Model):
    _name = 'unispice.packing.line'
    _description = 'Detalle embalaje Producto terminado'
    lote_id = fields.Many2one(comodel_name='stock.production.lot', string='Lote Producto terminado')
    producto_id = fields.Many2one(comodel_name='product.product', string='Producto')
    cantidad = fields.Float(string = 'Cantidad')
    peso_referencia = fields.Float(string = 'Peso referencia')
    peso_total = fields.Float(string = 'Peso total', compute='_get_peso_total')
    
    @api.depends('cantidad', 'peso_referencia')
    def _get_peso_total(self):
        for packing in self:
            packing.peso_total = packing.cantidad * packing.peso_referencia
