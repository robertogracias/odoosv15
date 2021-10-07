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


    
class integrador_category(models.Model):
    _inherit='product.category'
    code=fields.Integer("Codigo",select=True)

class integrador_user(models.Model):
    _inherit='res.users'
    code=fields.Integer("Codigo",select=True)

class integrador_partner(models.Model):
    _inherit='res.partner'
    nrc=fields.Char("NRC")
    nit=fields.Char("NIT",select=True)
    giro=fields.Char("Giro")
    razon_social=fields.Char("Razón social")

