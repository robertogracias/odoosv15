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

class unispice_packing(models.Model):
    _name = 'unispice.packing'
    _description = 'Embalaje Producto terminado'
