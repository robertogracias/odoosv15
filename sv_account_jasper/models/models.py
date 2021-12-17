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
            texto=''
            jasper=r.company_id.jasper
            if not jasper:
                jasper=self.env['odoosv.jasper'].search([('name','=','odoo')],limit=1)
            if jasper:
                if r.tipo_documento_id:
                    if r.tipo_documento_id.formato:
                        texto=jasper.create_link_report('/sv/reportes/transacciones',r.tipo_documento_id.formato,r.id,'pdf')
            r.formato_fiscal=texto


class jasrper_journal(models.Model):
    _inherit='account.journal'
    formato=fields.Char("Formato Preimpreso")
    numero_cheque_maximo=fields.Char("Último numero de queque")
    cheques_disponibles=fields.Integer("Cheques disponibles", compute='_get_disponible')

    @api.depends('check_next_number','numero_cheque_maximo')
    def _get_disponible(self):
        for r in self:
            resultado=0
            try:
                if r.check_next_number and r.numero_cheque_maximo:
                    a=int(r.check_next_number)
                    b=int(r.numero_cheque_maximo)
                    resultado=b-a
            except:
                print("Hubo un error")
            r.cheques_disponibles=resultado


class jasper_account_move(models.Model):
    _inherit='account.payment'
    impreso=fields.Boolean("Impreso")
    formato_fiscal=fields.Char("formato fiscal",compute='compute_fiscalreport',store=False)
    no_negociable=fields.Boolean("No Negociable")
    a_nombre_de=fields.Char("A nombre de ")

    def imprimir(self):
        for r in self:
            r.impreso=True
    
    def compute_fiscalreport(self):
        for r in self:
            texto=''
            jasper=r.company_id.jasper
            if not jasper:
                jasper=self.env['odoosv.jasper'].search([('name','=','odoo')],limit=1)
            if jasper:
                if r.journal_id.formato:
                    texto=jasper.create_link_report('/sv/reportes/transacciones',r.journal_id.formato,r.id,'pdf')
            r.formato_fiscal=texto