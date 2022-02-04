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
from datetime import timedelta
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


class jpc_cultivo(models.Model):
    _name='jpc.cultivo'
    _description='Cultivo'
    name='Cultivo'

class jpc_cuenta_analiticas(models.Model):
    _inherit='account.analytic.account'
    tipo=fields.Selection(selection=[('Hacienda','Hacienda'),('Lote','Lote'),('Cultivo','Cultivo'),('Otro','Otro')],string="Tipo Cuenta Analitica")
    cultivo_id=fields.Many2one('jpc.cultivo',string='Cultivo')
    parent_id=fields.Many2one('account.analytic.account',string='Parent')

class jpc_reporte_jornada(models.Model):
    _name='jpc.reporte.jornal'
    _inherit='mail.thread'
    _description='Reporte de jornal por dia'
    name=fields.Char("Reporte",compute="_get_name")
    fecha=fields.Date("Fecha del reporte")
    supervisor_id=fields.Many2one('hr.employee',string='Supervisor')
    hacienda_id=
    cuenta_analitica_id=fields.Many2one('account.analytic.account',string='Centro de costo')
    hacienda_id=fields.Many2one('account.analytic.account',string='Hacienda')
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
    catorcena_id=fields.Many2one('jpc.reporte.jornal.catorcena',string='Catorcena')

    @api.depends('product_id', 'quantity','price_unit')
    def _get_total(self):
        for r in self:
            r.total=r.quantity*r.price_unit
    
    @api.onchange('product_id')
    def onchange_product(self):
        for r in self:
            if r.product_id:
                r.price_unit=r.product_id.standard_price



class jpc_reporte_catorcena(models.Model):
    _name='jpc.reporte.jornal.catorcena'
    _inherit='mail.thread'
    _description='Reporte de jornal por catorcena'
    name=fields.Char('Planilla')
    fecha1=fields.Date('Desde')
    fecha2=fields.Date('Hasta')
    cultivo_id=fields.Many2one('jpc.cultivo',string='Cultivo')
    dia1=fields.Date('D1',compute='calcular_dia')
    dia2=fields.Date('D2',compute='calcular_dia')
    dia3=fields.Date('D3',compute='calcular_dia')
    dia4=fields.Date('D4',compute='calcular_dia')
    dia5=fields.Date('D5',compute='calcular_dia')
    dia6=fields.Date('D6',compute='calcular_dia')
    dia7=fields.Date('D7',compute='calcular_dia')
    dia8=fields.Date('D8',compute='calcular_dia')
    dia9=fields.Date('D9',compute='calcular_dia')
    dia10=fields.Date('D10',compute='calcular_dia')
    dia11=fields.Date('D11',compute='calcular_dia')
    dia12=fields.Date('D12',compute='calcular_dia')
    dia13=fields.Date('D13',compute='calcular_dia')
    dia14=fields.Date('D14',compute='calcular_dia')
    dia15=fields.Date('D15',compute='calcular_dia')
    dia16=fields.Date('D16',compute='calcular_dia')
    dia0=fields.Date('D0',compute='calcular_dia')


    def calcular(self):
        for r in self:
            lista=self.env['jpc.reporte.jornal.item'].search([('cuenta_analitica_id.cultivo','=',r.cultivo_id.id),('cuenta_analitica_id.cultivo','=',r.cultivo_id.id),('fecha','>=',r.fecha1),('fecha','<=',r.fecha2)])
            for l in lista:
                l.write({'catorcena_id':r.id})


    def calcular_dia(self):
        for r in self:
            r.dia1=timedelta(days=0)
            r.dia2=timedelta(days=1)
            r.dia3=timedelta(days=2)
            r.dia4=timedelta(days=3)
            r.dia5=timedelta(days=4)
            r.dia6=timedelta(days=5)
            r.dia7=timedelta(days=6)
            r.dia8=timedelta(days=7)
            r.dia9=timedelta(days=8)
            r.dia10=timedelta(days=9)
            r.dia11=timedelta(days=10)
            r.dia12=timedelta(days=11)
            r.dia13=timedelta(days=12)
            r.dia14=timedelta(days=13)
            r.dia15=timedelta(days=14)
            r.dia16=timedelta(days=15)

    

class jpc_reporte_catorcena_line(models.Model):
    _name='jpc.reporte.jornal.catorcena.line'    
    catorcena_id=fields.Many2one('jpc.cultivo',string='Cultivo')
    empleado_id=fields.Many2one('res.partner',string='Empleado')





