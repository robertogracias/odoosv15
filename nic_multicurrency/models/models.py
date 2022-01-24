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




class nic_currency_rate(models.Model):
    _inherit='res.currency.rate'
    inverse_rate=fields.Float("Tasa Invertida")

    @api.onchange('inverse_rate')
    def change_inverse(self):
        for r in self:
            if r.inverse_rate!=0:
                r.rate=1/r.inverse_rate