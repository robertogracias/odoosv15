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



class odoo_jasper_company(models.Model):
    _inherit='res.company'
    jasper = fields.Many2one('odoosv.jasper',string='Servidor de reportes asociado',help='Libro asociado')


class odoosv_jasper(models.Model):
    _name='odoosv.jasper'
    _description='Servidor de jasperserver'
    name=fields.Char("Nombre")
    url=fields.Char("URL")
    usuario=fields.Char("Usuario")
    password=fields.Char("Password")
    locate=fields.Char("Localizacion")
    timezone=fields.Char("Time Zone")

    def create_link(self,servidor,ruta,reporte,id=None,output=None):
        jasper=self.env['odoosv.jasper'].searhc([('name','=',servidor)],limit=1)
        link=''
        if jasper:
            link=jasper.url+"/flow.html?_flowId=viewReportFlow&standAlone=true&j_acegi_security_check?"
            link=link+"&j_username="+jasper.usuario
            link=link+"&j_password="+jasper.password
            link=link+"&userLocale="+jasper.locate+"&_flowId=viewReportFlow"
            if output:
                link=link+"&output="+output
            link=link+"&ParentFolderUri="+ruta
            link=link+"&reportUnit="+ruta+"/"+reporte
            link=link+"&decorate=no"
            link=link+"&userTimezone="+jasper.timezone
            link=link+"&companyId="+str(self.env.user.company_id.id)
            if id:
                link=link+"&id="+str(id)
        return link
    
    def create_link_report(self,ruta,reporte,id=None,output=None):
        for jasper in self:
            link=''
            if jasper:
                link=jasper.url+"/flow.html?_flowId=viewReportFlow&standAlone=true&j_acegi_security_check?"
                link=link+"&j_username="+jasper.usuario
                link=link+"&j_password="+jasper.password
                link=link+"&userLocale="+jasper.locate+"&_flowId=viewReportFlow"
                if output:
                    link=link+"&output="+output
                link=link+"&ParentFolderUri="+ruta
                link=link+"&reportUnit="+ruta+"/"+reporte
                link=link+"&decorate=no"
                link=link+"&userTimezone="+jasper.timezone
                link=link+"&companyId="+str(self.env.user.company_id.id)
                if id:
                    link=link+"&id="+str(id)
            return link




class odoosv_reporte(models.Model):
    _name='odoosv.reporte'
    _description='Reporte externo'
    name=fields.Char('Reporte')
    reporte=fields.Char('Id del Reporte')
    ruta=fields.Char('Ruta')
    jasper = fields.Many2one('odoosv.jasper',string='Servidor de reportes asociado',help='Libro asociado')

    url=fields.Char('Link',compute='get_link',store=False)

    @api.depends('reporte','ruta','jasper')
    def get_link(self):
        for r in self:
            if r.jasper:
                r.url=r.jasper.create_link_report(r.ruta,r.reporte)
            else:
                r.url=''