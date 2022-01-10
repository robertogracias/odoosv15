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


#Sucursales
class sucursales_sucursal(models.Model):
    _name='odoosv.caja'
    _description='Definicion de caja'
    _inherit= ['mail.thread']
    name=fields.Char('Caja')
    location_id=fields.Many2one(comodel_name='stock.location', string="Ubicacion")
    warehouse_id=fields.Many2one(comodel_name='stock.warehouse', string="Almacen")
    picking_type_id=fields.Many2one(comodel_name='stock.picking.type', string="Transferencia de cliente")
    analytic_account_id=fields.Many2one(comodel_name='account.analytic.account', string="Cuenta analitica")
    serie_ids=fields.One2many(comodel_name='odoosv.serie',inverse_name='caja_id',string="Series")
    


class sucursales_series(models.Model):
    _name='odoosv.serie'
    _description='Series por documento'
    name=fields.Char('tipo documento')
    tipo_documento_id=fields.Many2one('odoosv.fiscal.document',string="Tipo de Documento",ondelete="restrict")
    sv_sequence_id=fields.Many2one('ir.sequence',string="Numeracion",ondelete="restrict")
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja")
    serie=fields.Char('Serie')

    
class sucursales_user(models.Model):
    _inherit='res.users'
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja")
    
    
class sucursales_sale_order(models.Model):
    _inherit='sale.order'
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja")
    
    @api.onchange('caja_id')
    def get_warehouse_id(self):
        for r in self:
            if r.caja_id:
                if r.caja_id.warehouse_id:
                    r.warehouse_id=r.caja_id.warehouse_id.id
    
class sucursales_account_move(models.Model):
    _inherit='account.move'
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja", default=lambda self: self.env.user.caja_id)
    cierre_id=fields.Many2one(comodel_name='odoosv.cierre', string="Cierre")
    serie=fields.Char('Serie')
    
    def set_access_for_caja(self):
        self.ensure_one()
        self.able_to_modify_caja = self.env['res.users'].has_group('sv_caja.odoosv_cambia_caja')

    able_to_modify_caja = fields.Boolean(compute=set_access_for_caja, string='puede modificar caja')

class sucursales_account_move_line(models.Model):
    _inherit='account.move.line'
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja", related='move_id.caja_id',store=True)


    def set_analityc(self):
        for r in self:
            if not r.analytic_account_id:
                if r.caja_id:
                    if r.caja_id.analytic_account_id:
                        r.analytic_account_id=r.caja_id.analytic_account_id.id

class sucursales_account_payment(models.Model):
    _inherit='account.payment'
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Caja", default=lambda self: self.env.user.caja_id)
    cierre_id=fields.Many2one(comodel_name='odoosv.cierre', string="Cierre")
    facturas=fields.Char("Facturas",compute='calcular_facturas',store=False)


    def calcular_facturas(self):
        for r in self:
            text=''
            for l in r.reconciled_invoice_ids:
                if l.tipo_documento_id:
                    text=text+' '+l.tipo_documento_id.name
                    if l.doc_numero:
                        text=text+':'+l.doc_numero+ '  '
            r.facturas=text
        
    def set_access_for_caja(self):
        self.ensure_one()
        self.able_to_modify_caja = self.env['res.users'].has_group('sv_caja.odoosv_cambia_caja')

    able_to_modify_caja = fields.Boolean(compute=set_access_for_caja, string='puede modificar caja')
    

    
#Cierre
class sucursales_cierre(models.Model):
    _name='odoosv.cierre'
    _description='Cierre'
    _inherit= ['mail.thread']
    name=fields.Char("Cierre")
    caja_id=fields.Many2one(comodel_name='odoosv.caja', string="Sucursal")
    comentario=fields.Text("Comentario")
    fecha=fields.Date('Fecha')
    total_facturado=fields.Float("Total Facturado")
    total_pagado=fields.Float("Total Pagado")
    inicio=fields.Datetime("Hora de inicio")
    final=fields.Datetime("Hora de apertura")
    cierrepago_ids=fields.One2many(comodel_name='odoosv.cierre.pago',inverse_name='cierre_id',string="Formas de pago")
    factura_ids=fields.One2many(comodel_name='account.move',inverse_name='cierre_id',string="Facturas")
    pago_ids=fields.One2many(comodel_name='account.payment',inverse_name='cierre_id',string="Pagos")
    remesa_ids=fields.One2many(comodel_name='odoosv.cierre.remesa',inverse_name='cierre_id',string="Remesas")
    estado=fields.Selection(selection=[('Creado', 'Creado')
                                    ,('Confirmado', 'Confirmado')]
                                    , string='Estado',required=True,default='Creado',track_visibility=True)
    
    
    def liberar(self):
        for record in self:
            facturas=self.env['account.move'].search([('cierre_id','=',record.id)])
            for factura in facturas:
                factura.write({'cierre_id':False})
            pagos=self.env['account.payment'].search([('cierre_id','=',record.id)])
            for pago in pagos:
                pago.write({'cierre_id':False})
            cierres=self.env['odoosv.cierre.pago'].search([('cierre_id','=',record.id)])
            for cierre in cierres:
                cierre.unlink()
            record.write({'total_facturado':0})
            record.write({'total_pagado':0})
    
    def cerrar(self):
        for record in self:
            record.write({'estado','Cerrado'})
            
    
    def calcular(self):
        for record in self:
            current=record.fecha
            dia=int(datetime.strftime(current, '%d'))
            mes=int(datetime.strftime(current, '%m'))
            anio=int(datetime.strftime(current, '%Y'))
            #resetenado los valores
            total_facturado=0
            total_pagado=0
            cash_sacado=0
            #liberando
            facturas=self.env['account.move'].search([('cierre_id','=',record.id)])
            for factura in facturas:
                factura.write({'cierre_id':False})
            pagos=self.env['account.payment'].search([('cierre_id','=',record.id)])
            for pago in pagos:
                pago.write({'cierre_id':False})
            cierres=self.env['odoosv.cierre.pago'].search([('cierre_id','=',record.id)])
            for cierre in cierres:
                cierre.unlink()
            remesas=self.env['odoosv.cierre.remesa'].search([('cierre_id','=',record.id)])
            for remesa in remesas:
                remesa.unlink()
            #listando las ordenes de este diari
            hoy_1=datetime(anio,mes,dia,0,0,1)
            hoy_2=datetime(anio,mes,dia,23,59,59)
            hoy_1=hoy_1+timedelta(hours=6)
            hoy_2=hoy_2+timedelta(hours=6)
            #facturas=env['account.move'].search([('invoice_date','>=',hoy_1),('invoice_date','<=',hoy_2),('type','=','out_invoice'),('state','!=','draft'),('state','!=','cancel')])
            facturas=self.env['account.move'].search([('invoice_date','=',current),('caja_id','=',record.caja_id.id),('move_type','=','out_invoice'),('state','!=','draft'),('state','!=','cancel')])
            for factura in facturas:
                if not factura.cierre_id:
                    factura.write({'cierre_id':record.id})
                    total_facturado=total_facturado+factura.amount_total
            #pagos=env['account.payment'].search([('payment_date','>=',hoy_1),('payment_date','<=',hoy_2),('payment_type','=','inbound'),('state','!=','draft'),('state','!=','cancelled')])
            pagos=self.env['account.payment'].search([('date','=',current),('caja_id','=',record.caja_id.id),('payment_type','=','inbound'),('state','!=','draft'),('state','!=','cancelled')])
            for pago in pagos:
                if not pago.cierre_id:
                    pago.write({'cierre_id':record.id})
                    total_pagado=total_pagado+pago.amount
            #pagos2=env['account.payment'].search(['&',('payment_date','>=',hoy_1),('payment_date','<=',hoy_2),('payment_type','=','outbound'),('state','!=','draft'),('state','!=','cancelled')])
            pagos2=self.env['account.payment'].search([('date','=',current),('caja_id','=',record.caja_id.id),('payment_type','=','outbound'),('state','!=','draft'),('state','!=','cancelled')])
            for pago in pagos2:
                if not pago.cierre_id:
                    if pago.journal_id.type=='cash':
                        pago.write({'cierre_id':record.id})
                        total_pagado=total_pagado-pago.amount
                        cash_sacado=cash_sacado+pago.amount
            #remesas=env['account.payment'].search(['&',('payment_date','>=',hoy_1),('payment_date','<=',hoy_2),('payment_type','=','transfer'),('state','!=','draft'),('state','!=','cancelled')])
            remesas=self.env['account.payment'].search([('date','=',current),('caja_id','=',record.caja_id.id),('payment_type','=','transfer'),('state','!=','draft'),('state','!=','cancelled')])
            for remesa in remesas:
                dic={}
                dic['origen']=remesa.journal_id.id
                dic['destino']=remesa.destination_journal_id.id
                dic['monto']=remesa.amount
                dic['cierre_id']=record.id
                env['odoosv.cierre.remesa'].create(dic)
            diarios=self.env['account.journal'].search([('id','>',0)])
            for diario in diarios:
                total_diario=0.0
                pagos3=self.env['account.payment'].search(['&',('cierre_id','=',record.id),('payment_type','=','inbound'),('journal_id','=',diario.id)])
                for pago2 in pagos3:
                    total_diario=total_diario+pago2.amount
                #if diario.type=='cash':
                #  pagos4=env['account.payment'].search(['&',('cierre_id','=',record.id),('payment_type','=','outbound'),('journal_id','=',diario.id)])
                #  for pago2 in pagos4:
                #    total_diario=total_diario-pago2.amount
                if total_diario!=0:
                    self.env['odoosv.cierre.pago'].create({'name':diario.name,'cierre_id':record.id,'journal_id':diario.id,'monto':total_diario})
                    #raise ValidationError("hay ordenes: %s" %total_venta)
            record.write({'total_facturado':total_facturado,'total_pagado':total_pagado,'inicio':hoy_1,'final':hoy_2})
    

class sucursales_cierre_pago(models.Model):
    _name='odoosv.cierre.pago'
    _description='Pagos en el cierre'
    name=fields.Char("Cierre")
    monto=fields.Float("Monto")
    journal_id=fields.Many2one(comodel_name='account.journal', string="Metodo de pago")
    cierre_id=fields.Many2one(comodel_name='odoosv.cierre', string="Cierre")


class sucursales_cierre_Remesa(models.Model):
    _name='odoosv.cierre.remesa'
    _description='Remesas en el cierre'
    name=fields.Char("Remesa")
    origen_id=fields.Many2one(comodel_name='account.journal', string="Origen")
    destino_id=fields.Many2one(comodel_name='account.journal', string="Destino")
    cierre_id=fields.Many2one(comodel_name='odoosv.cierre', string="Cierre")
    monto=fields.Float("Monto")
    