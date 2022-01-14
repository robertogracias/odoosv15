# -*- coding: utf-8 -*-
# from odoo import http
import logging
import pprint
import werkzeug
import json
import requests
import time

from datetime import datetime
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

class basculas(http.Controller):

    @http.route('/gestion-venta', auth='none')
    def get_gestion(self, **kw):
        return '[{"code":"EV","description":"Ejecutivo de Ventas"},{"code":"SV","description":"Soporte de Ventas"}]'
    
    @http.route('/bascula', auth='none')
    def registro(self, **kwargs):
        name=None
        url=None
        for field_name, field_value in kwargs.items():
            if field_name=='name':
                name=field_value
            if field_name=='url':
                url=field_value
        if name:
            bascula=request.env['basculas.bascula'].sudo().search([('name','=',name)],limit=1)
            if bascula:
                if url!=bascula.url:
                    bascula.write({'url':url,'last_ping':datetime.now()})
                else:
                    bascula.write({'last_ping':datetime.now()})
            else:
                bascula=request.env['basculas.bascula'].sudo().create({'name':name,'url':url,'port':'comm1','baudrate':9600,'parity':0,'parse':''})
            dic={}
            dic['name']=bascula.name
            dic['url']=bascula.url
            dic['port']=bascula.port
            dic['baudrate']=bascula.baudrate
            dic['bits']=bascula.bits
            dic['parity']=bascula.parity
            dic['parse']=bascula.parse

            return json.dumps(dic)
        return json.dumps('error')

    