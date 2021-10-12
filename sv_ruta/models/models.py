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




class odoosv_partner(models.Model):
    _inherit='res.partner'
    ruta_id=fields.Many2one(comodel_name='odoosv.ruta',string='Ruta')
    prioridad=fields.Selection(selection=[('ninguna','Ninguna'),('baja','Baja'),('media','Media'),('alta','Alta')],string="Pioridad en la ruta")

class odoosv_move(models.Model):
    _inherit='account.move'
    ruta_id=fields.Many2one(comodel_name='odoosv.ruta',string='Ruta',related='partner_shipping_id.ruta_id')

class odoosv_saleorder(models.Model):
    _inherit='sale.order'
    ruta_id=fields.Many2one(comodel_name='odoosv.ruta',string='Ruta',related='partner_shipping_id.ruta_id')

class odoosv_referencia(models.Model):
    _name='odoosv.ruta'
    _description='Ruta'
    name=fields.Char("Nombre")

