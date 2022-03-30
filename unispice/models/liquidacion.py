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


class unispice_recepcion(models.Model):
    _name='unispice.liquidacion.batch'
    _inherit='mail.thread'
    _description='Liquidacion'

    desde=fields.Date("Desde")
    hasta=fields.Date("Hasta")
    name=fields.Char("Liquidacion")
    boleta_ids=fields.One2many(comodel_name='unispice.recepcion', string='Boletas',inverse_name='liquidacion_batch_id')
    liquidacion_ids=fields.One2many(comodel_name='unispice.liquidacion', string='Boletas',inverse_name='liquidacion_batch_id')



#Clase para la liquidacion de lotes
class unispice_recepcion(models.Model):
    _name='unispice.liquidacion'
    _inherit='mail.thread'
    _description='Liquidacion Por proveedor'

    proveedor_id=fields.Many2one(comodel_name='res.partner', string='Proveedor')
    state=fields.Selection(selection=[('draft','Borrador'),('Cerrado','Cerrado'),('SAP','Expportada a SAP'),('Cancelada','Cancelada')],string="Estado",default='draft',tracking=True)
    boleta_ids=fields.One2many(comodel_name='unispice.recepcion', string='Boletas',inverse_name='liquidacion_id')
    liquidacion_batch_id=fields.Many2one(comodel_name='unispice.liquidacion.batch', string='Liquidacion batch')
    descuento_ids=fields.One2many(comodel_name='unispice.liquidacion.descuento', string='Descuentos',inverse_name='liquidacion_id')



class unispice_reception_line(models.Model):
    _name='unispice.liquidacion.descuento'
    _description='Costo de la liquidacion'
    name=fields.Char('Costo')
    product_id=fields.Many2one(comodel_name='product.Product', string='Concepto')
    descuento=fields.Float("descuento")
    liquidacion_id=fields.Many2one(comodel_name='unispice.liquidacion', string='Liquidacion')