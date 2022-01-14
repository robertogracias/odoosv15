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


class bascula(models.Model):
    _name='basculas.bascula'
    _inherit='mail.thread'
    _description='Bascula'
    name=fields.Char("Bascula",tracking=True)
    last_ping=fields.Datetime("Ultimo ping")
    state=fields.Selection(selection=[('new','Nuevo'),('online','En Lina'),('offline','Fuera de linea')],store=False,compute='get_state')
    port=fields.Char("Puerto",tracking=True)
    baudrate=fields.Integer("Baud Rate",tracking=True)
    bits=fields.Integer("Bits",tracking=True)
    parity=fields.Integer("Paridad",tracking=True)
    parse=fields.Char("Parser",tracking=True)
    ultima_lectura=fields.Float("Ultima Lectura",digits=(20, 4))
    url=fields.Char("URL")
    url_reload=fields.Text("Url para Reload",compute='calcular_urls')
    url_get=fields.Text("Url para obtener datos",compute='calcular_urls')

    def calcular_urls(self):
        for r in self:
            if r.url:
                r.url_reload='<a href="'+r.url+'?a=reload" >Recargar</a>'
                r.url_get='<a href="'+r.url+'?a=get" >Leer</a>'
    def get_state(self):
        for r in self:
            r.state='new'

    def leer(self):
        for r in self:
            url=r.url+'?a=get'
            response = requests.get(url)
            try:
                r.ultima_lectura=float(response.text)
            except: 
                r.ultima_lectura=0.0


    




    

