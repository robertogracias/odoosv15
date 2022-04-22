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
    name = fields.Char(sting = 'Packing number')
    lote_pallet = fields.Char(string = 'Lote Pallet')
    fecha = fields.Datetime(string = 'Fecha')

    # Detalle
    packing_line_ids = fields.One2many(string = 'Productos', comodel_name='unispice.packing.line', inverse_name='packing_line_id')

    # Misc.
    status = fields.Selection(
        string = "Estado"
        , selection = [('draft', 'Borrador'), ('done', 'Confirmado'), ('cancel', 'Cancelado')]
        , default = 'draft')

    # 'Materia Prima' in r.product_id.categ_id.display_name


class unispice_packing_line(models.Model):
    _name = 'unispice.packing.line'
    _description = 'Detalle embalaje Producto terminado'
    packing_line_id = fields.Many2one(string = 'Producto del embalaje', comodel_name = 'unispice.packing')
    lote_id = fields.Many2one(string='Lote Producto terminado', comodel_name='stock.production.lot')
    producto_id = fields.Many2one(string='Producto', comodel_name='product.product')
    cantidad = fields.Float(string = 'Cantidad')
    peso_referencia = fields.Float(string = 'Peso referencia')
    peso_total = fields.Float(string = 'Peso total', compute='_get_peso_total')
    
    @api.depends('cantidad', 'peso_referencia')
    def _get_peso_total(self):
        for packing in self:
            packing.peso_total = packing.cantidad * packing.peso_referencia
