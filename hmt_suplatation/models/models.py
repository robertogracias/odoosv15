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
from datetime import datetime, timedelta,date
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


#referencia al usuario de suplantacion
class suplantantion_user(models.Model):
    _inherit='res.users'
    suplantation_user=fields.Many2one(comodel_name='res.users', string="Ubicacion")
    
class sucursales_account_move(models.Model):
    _inherit='account.move'
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja", default=lambda self: self.env.user.suplantation_user.caja_id if self.env.user.suplantation_user else self.env.user.caja_id)
    invoice_user_id=fields.Many2one(comodel_name='res.users', string="Vendedor", default=lambda self: self.env.user.suplantation_user if self.env.user.suplantation_user else self.env.user)
    mirror_date=fields.Date("Fecha",store=False,compute='get_mirror_fields')
    mirror_price_list=fields.Char("Lista de Precios",store=False,compute='get_mirror_fields')

    @api.depends('invoice_date','pricelist_id')
    def get_mirror_fields(self):
        for r in self:
            r.mirror_date=r.invoice_date
            if r.pricelist_id:
                r.mirror_price_list=r.pricelist_id.name
            else:
                r.mirror_price_list=''

class sucursales_account_move(models.Model):
    _inherit='account.move.line'
    mirror_price_unit=fields.Float("Precio Unitario",store=False,compute='get_mirror_fields')

    @api.depends('price_unit')
    def get_mirror_fields(self):
        for r in self:
            r.mirror_price_unit=r.price_unit

    
class sucursales_account_payment(models.Model):
    _inherit='account.payment'
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja", default=lambda self: self.env.user.suplantation_user.caja_id if self.env.user.suplantation_user else self.env.user.caja_id)

class hmt_tipo_movimiento(models.Model):
    _inherit='stock.picking.type'
    user_id=fields.Many2one(comodel_name='res.users', string="Usuario")


class hmt_movimiento(models.Model):
    _inherit='stock.picking'
    user_id=fields.Many2one(comodel_name='res.users', string="Usuario", default=lambda self: self.env.user.suplantation_user if self.env.user.suplantation_user else self.env.user)

    

class hmt_bodega(models.Model):
    _inherit='stock.location'
    principal=fields.Boolean("Ubicacion Princial")

class hmt_vendedor(models.Model):
    _name="hmt.vendedor"
    _inherit=['mail.thread']
    _descriptio="Vendedor de HMT para ser suplantado"
    name=fields.Char("Vendedor",tracking=True)
    pin=fields.Char("PIN")
    analytic_account_id=fields.Many2one(comodel_name='account.analytic.account', string="Cuenta analitica",tracking=True)
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja",tracking=True)
    warehouse_id=fields.Many2one(comodel_name='stock.warehouse', string="Almacen",tracking=True)
    user_id=fields.Many2one(comodel_name='res.users', string="Usuario",tracking=True)
    state=fields.Selection(selection=[('new','Nuevo'),('habilitado','Habilitado'),('deshabilitado','Deshabilitado')],default='new')

    def habilitar(self):
        for r in self:
            if not r.warehouse_id:
                dic={}
                dic['name']='Bodega:'+r.name
                dic['code']='V'+str(r.id)
                dic['reception_steps']='one_step'
                dic['delivery_steps']='ship_only'
                dic['buy_to_resupply']=False
                wh=self.env['stock.warehouse'].create(dic)
                r.warehouse_id=wh.id
            if not r.caja_id:
                dic={}
                dic['name']='Caja: '+r.name
                dic['warehouse_id']=r.warehouse_id.id
                dic['location_id']=r.warehouse_id.lot_stock_id.id
                dic['entregar_producto']=True
                if r.analytic_account_id:
                    dic['analytic_account_id']=r.analytic_account_id.id
                caja=self.env['odoosv.caja'].create(dic)
                r.caja_id=caja.id
            if not r.user_id:
                dic={}
                dic['name']=r.name
                dic['login']=r.name+'@hmt.com'
                dic['email']=r.name+'@hmt.com'
                dic['sel_groups_1_9_10']='9'
                dic['caja_id']=r.caja_id.id
                user=self.env['res.users'].create(dic)
                r.user_id=user.id
            bodega_principal=self.env['stock.location'].search([('principal','=',True)],limit=1)
            dic1={}
            dic1['name']='Recarga:'+r.name
            dic1['sequence_code']='R'+str(r.id)
            dic1['warehouse_id']=r.warehouse_id.id
            dic1['code']='internal'
            dic1['user_id']=r.user_id.id
            dic1['default_location_src_id']=bodega_principal.id
            dic1['default_location_dest_id']=r.warehouse_id.lot_stock_id.id
            self.env['stock.picking.type'].create(dic1)
            dic2={}
            dic2['name']='Liquidacion:'+r.name
            dic2['sequence_code']='L'+str(r.id)
            dic2['warehouse_id']=r.warehouse_id.id
            dic2['code']='internal'
            dic2['user_id']=r.user_id.id
            dic2['default_location_dest_id']=bodega_principal.id
            dic2['default_location_src_id']=r.warehouse_id.lot_stock_id.id
            self.env['stock.picking.type'].create(dic2)
            dic3={}
            dic3['name']='Devolucion:'+r.name
            dic3['sequence_code']='D'+str(r.id)
            dic3['warehouse_id']=r.warehouse_id.id
            dic3['code']='incoming'
            dic3['user_id']=r.user_id.id
            dic3['default_location_src_id']=self.env.ref('stock.stock_location_customers').id
            dic3['default_location_dest_id']=r.warehouse_id.lot_stock_id.id
            self.env['stock.picking.type'].create(dic3)
            r.state='habilitado'



    

class hmt_login(models.Model):
    _name='hmt.login'
    _description='Login por suplantacion'
    name=fields.Char("name")
    vendedor_id=fields.Many2one(comodel_name='hmt.vendedor', string="Vendedor")
    pin=fields.Char("PIN")
    mensaje=fields.Char("Mensaje")



    def login(self):
        self.ensure_one()
        if self.vendedor_id.pin==self.pin:
            user=self.env.user
            user.sudo().write({'suplantation_user':self.vendedor_id.user_id})
            self.mensaje='LOGEADO CORRECTAMENTE'
        else:
            raise ValidationError('El pin no es el correcto')
