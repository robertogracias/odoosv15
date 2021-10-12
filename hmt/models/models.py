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




class hmt_restriccion(models.Model):
    _name='hmt.product.restriccion'
    _description='Restriccion sobre la venta de produccto'
    name=fields.Char("Nombre")
    partner_id=fields.Many2one(comodel_name='res.partner',string='Cliente')
    ruta_id=fields.Many2one(comodel_name='odoosv.ruta',string='Ruta')
    canal_id=fields.Many2one(comodel_name='odoosv.canal',string='Canal')
    product_id=fields.Many2one(comodel_name='product.template',string='Producto')


class hmt_producto(models.Model):
    _inherit='product.template'
    restriccion_ids=fields.One2many(comodel_name='hmt.product.restriccion',inverse_name='product_id',string='Restricciones')


class hmt_saleorder(models.Model):
    _inherit='sale.order'
    
    @api.constrains('partner_id','ruta_id','canal_id')
    def _check_restriciones(self):
        for r in self:
            for l in r.order_line:
                for c in l.product_id.product_tmpl_id.restriccion_ids:
                    if c.partner_id:
                        if c.ruta_id:
                            if c.canal_id:
                                if r.partner_id.id==c.partner_id.id and r.ruta_id.id==c.ruta_id.id and r.canal_id.id==c.canal_id.id:
                                    raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+ ' ruta:'+c.ruta_id.name+ ' canal:'+c.canal_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                            else:
                                if r.partner_id.id==c.partner_id.id and r.ruta_id.id==c.ruta_id.id:
                                    raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+ ' ruta:'+c.ruta_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                        else:
                            if c.canal_id:
                                if r.partner_id.id==c.partner_id.id  and r.canal_id.id==c.canal_id.id:
                                    raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+' canal:'+c.canal_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                            else:
                                if r.partner_id.id==c.partner_id.id:
                                    raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                    else:
                        if c.ruta_id:
                            if c.canal_id:
                                if r.ruta_id.id==c.ruta_id.id and r.canal_id.id==c.canal_id.id:
                                    raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+ ' ruta:'+c.ruta_id.name+ ' canal:'+c.canal_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                            else:
                                if r.ruta_id.id==c.ruta_id.id :
                                    raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+ ' ruta:'+c.ruta_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                        else:
                            if c.canal_id:
                                if r.canal_id.id==c.canal_id.id:
                                    raise ValidationError(' canal:'+c.canal_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')



class hmt_saleorder_line(models.Model):
    _inherit='sale.order.line'
    
    @api.constrains('product_id')
    def _check_restriciones(self):
        for l in self:
            r=l.order_id
            for c in l.product_id.product_tmpl_id.restriccion_ids:
                if c.partner_id:
                    if c.ruta_id:
                        if c.canal_id:
                            if r.partner_id.id==c.partner_id.id and r.ruta_id.id==c.ruta_id.id and r.canal_id.id==c.canal_id.id:
                                    raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+ ' ruta:'+c.ruta_id.name+ ' canal:'+c.canal_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                        else:
                            if r.partner_id.id==c.partner_id.id and r.ruta_id.id==c.ruta_id.id:
                                    raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+ ' ruta:'+c.ruta_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                    else:
                        if c.canal_id:
                            if r.partner_id.id==c.partner_id.id  and r.canal_id.id==c.canal_id.id:
                                raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+' canal:'+c.canal_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                        else:
                            if r.partner_id.id==c.partner_id.id:
                                raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                else:
                    if c.ruta_id:
                        if c.canal_id:
                            if r.ruta_id.id==c.ruta_id.id and r.canal_id.id==c.canal_id.id:
                                raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+ ' ruta:'+c.ruta_id.name+ ' canal:'+c.canal_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                        else:
                            if r.ruta_id.id==c.ruta_id.id :
                                raise ValidationError('El producto '+l.product_id.product_tmpl_id.name+ ' ruta:'+c.ruta_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')
                    else:
                        if c.canal_id:
                            if r.canal_id.id==c.canal_id.id:
                                raise ValidationError(' canal:'+c.canal_id.name+' No puede ser vendido por restricciones de cliente, ruta  y canal')

