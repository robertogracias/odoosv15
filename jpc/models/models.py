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


class jpc_approval_request(models.Model):
    _inherit='approval.request'
    account_move_id=fields.Many2one(comodel_name='account.move',string='Factura')


class jpc_cuenta_analiticas(models.Model):
    _inherit='account.analytic.account'
    tipo=fields.Selection(selection=[('Hacienda','Hacienda'),('Lote','Lote'),('Cultivo','Cultivo'),('Otro','Otro')],string="Tipo Cuenta Analitica")


class jpc_reporte_jornada(models.Model):
    _name='jpc.reporte.jornal'
    _inherit='mail.thread'
    _description='Reporte de jornal por dia'
    name=fields.Char("Reporte",compute="_get_name")
    fecha=fields.Date("Fecha del reporte")
    supervisor_id=fields.Many2one('hr.employee',string='Supervisor')
    cuenta_analitica_id=fields.Many2one('account.analytic.account',string='Centro de costo')
    item_ids=fields.One2many(comodel_name='jpc.reporte.jornal.item',inverse_name='jornada_id',string='Detalles')
    move_id=fields.Many2one('account.move',string='Partida')
    state=fields.Selection(selection=[('borrador','Borrador'),('Aprobado','Aprobado')],string="Estado",default="borrador")


    def _get_name(self):
        for r in self:
            r.name=str(r.fecha)

    def button_draft(self):
        for r in self:
            r.state='borrador'
            if r.move_id:
                r.move_id.button_draft()
                r.move_id.unlink()

    def button_aprobar(self):
        for r in self:
            dic={}
            dic['date']=r.fecha
            dic['ref']=r.name
            lines=[]
            for l in r.item_ids:
                #cargo:
                cargo={}
                cargo['product_id']=l.product_id.id
                cargo['name']=l.empleado_id.name+':'+l.product_id.name
                cargo['partner_id']=l.empleado_id.id
                cargo['analytic_account_id']=r.cuenta_analitica_id.id
                cargo['account_id']=l.product_id.categ_id.property_account_expense_categ_id.id
                cargo['credit']=0
                cargo['debit']=l.total
                cargo1=(0,0,cargo)
                lines.append(cargo1)
                #creando abono
                abono={}
                abono['name']=l.empleado_id.name+':'+l.product_id.name
                abono['partner_id']=l.empleado_id.id
                abono['analytic_account_id']=r.cuenta_analitica_id.id
                abono['account_id']=l.empleado_id.property_account_payable_id.id
                abono['credit']=l.total
                abono['debit']=0
                abono1=(0,0,abono)
                lines.append(abono1)
            dic['line_ids']=lines
            partida=self.env['account.move'].create(dic)
            r.move_id=partida.id
            r.state='Aprobado'


class jpc_reporte_jornada_detail(models.Model):
    _name='jpc.reporte.jornal.item'
    _description='Reporte de jornal por dia'
    name=fields.Char("Name")
    empleado_id=fields.Many2one('res.partner',string='Empleado')
    product_id=fields.Many2one('product.product',string='Servicio')
    quantity=fields.Float('Cantidad')
    price_unit=fields.Float('Costo unitario')
    total=fields.Float('Total', compute='_get_total',store=True)
    jornada_id=fields.Many2one('jpc.reporte.jornal',string='Detalles')
    fecha=fields.Date("Fecha del reporte",related='jornada_id.fecha',store=True)
    cuenta_analitica_id=fields.Many2one('account.analytic.account',string='Centro de costo',related='jornada_id.cuenta_analitica_id',store=True)

    @api.depends('product_id', 'quantity','price_unit')
    def _get_total(self):
        self.ensure_one()
        self.total=self.quantity*self.price_unit
    
    @api.onchange('product_id')
    def onchange_product(self):
        for r in self:
            if r.product_id:
                r.price_unit=r.product_id.standard_price



    

