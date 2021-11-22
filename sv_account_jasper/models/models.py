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



class jasper_account_move(models.Model):
    _inherit='account.move'
    impreso=fields.Boolean("Impreso")
    formato_fiscal=fields.Char("formato fiscal",compute='compute_fiscalreport',store=False)

    def imprimir(self):
        for r in self:
            r.impreso=True
    
    def compute_fiscalreport(self):
        for r in self:
            jasper=r.company_id.jasper
            if not jasper:
                jasper=self.env['odoosv.jasper'].search([('name','=','odoo')],limit=1)
            if jasper:
                if r.tipo_documento_id:
                    r.formato_fiscal=jasper.create_link_report('/sv/reportes/transacciones',r.tipo_documento_id.formato,r.id,'pdf')
