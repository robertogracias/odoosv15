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


class hmt_approval_request(models.Model):
    _inherit='approval.request'
    account_move_id=fields.Many2one(comodel_name='account.move',string='Factura')

class htm_company(models.Model):
    _inherit='res.company'
    terminos_generales_venta=fields.Text("Terminos generales en las ordenes de venta")
    formas_pago=fields.Text("Formas de pago")
    garantia=fields.Text("Garantia")
    notas=fields.Text("Notas")
    otros=fields.Text("Otros parametros")
    entrega=fields.Text("Tiempos de entrega")

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
    especificacion=fields.Text("Especificacion Tecnica")

class hmt_saleorder(models.Model):
    _inherit='sale.order'
    terminos_generales_venta=fields.Text("Terminos generales en las ordenes de venta",default=lambda self: self.env.user.company_id.terminos_generales_venta)
    formas_pago=fields.Text("Formas de pago",default=lambda self: self.env.user.company_id.formas_pago)
    garantia=fields.Text("Garantia",default=lambda self: self.env.user.company_id.garantia)
    notas=fields.Text("Notas",default=lambda self: self.env.user.company_id.notas)
    otros=fields.Text("Otros parametros",default=lambda self: self.env.user.company_id.otros)
    entrega=fields.Text("Tiempos de entrega",default=lambda self: self.env.user.company_id.entrega)


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


class hm_account_move(models.Model):
    _inherit='account.move'
    po_aprobacion=fields.Many2one(comodel_name='approval.request',string='Request')
    po_aprobacion_requierida=fields.Boolean(string="Requiere Aprobacion",compute="_requerir_aprobacion",store=False)
    po_aprobacion_state=fields.Selection(selection=[('new','Nuevo'),('pending','Enviado'),('approved','Aprobado'),('refused','Rechazado'),('cancel','Cancelado')],related='po_aprobacion.request_status',store=False)

    @api.depends('state', 'invoice_line_ids')
    def _requerir_aprobacion(self):
        for r in self:
            validar=False
            if r.move_type=='in_invoice':
                for l in r.invoice_line_ids:
                    if l.purchase_line_id:
                        if l.price_unit!=l.purchase_line_id.price_unit:
                            validar=True
            r.po_aprobacion_requierida=validar

    def solicitar_aprobacion_po(self):
        for r in self:
            if r.move_type=='in_invoice':
                validar=False
                for l in r.invoice_line_ids:
                    if l.purchase_line_id:
                        if l.price_unit!=l.purchase_line_id.price_unit:
                            validar=True
                    if validar:
                        if not r.po_aprobacion:
                            dic={}
                            dic['account_move_id']=r.id
                            dic['reason']='Los precios varian entre la orden de compra y la factrura'
                            modeldata = self.env['ir.model.data'].search([('module','=','hmt'),('name','=','sv_pofactura_approval')],limit=1)
                            categoria=self.env['approval.category'].browse(modeldata.res_id)
                            dic['category_id']=categoria.id
                            dic['name']='Aprobacion Factura '+r.name
                            request=self.env['approval.request'].create(dic)
                            r.po_aprobacion=request.id

    @api.constrains('state')
    def check_po_prices(self):
        for r in self:
            if r.state=='posted' and r.move_type=='in_invoice':
                validar=False
                for l in r.invoice_line_ids:
                    if l.purchase_line_id:
                        if l.price_unit!=l.purchase_line_id.price_unit:
                            validar=True
                if validar:
                    if r.po_aprobacion:
                        if r.po_aprobacion.request_status!='approved':
                            raise ValidationError('La factura requiere aprobacion por diferencia de precios')
                    else:
                        raise ValidationError('La factura requiere aprobacion por diferencia de precios')

