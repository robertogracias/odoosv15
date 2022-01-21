# -*- coding: utf-8 -*-


import base64
import json
import requests
import logging
import time
from datetime import datetime
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class unispice_company(models.Model):
    _inherit='res.company'
    internal_transfer_id=fields.Many2one(comodel_name='stock.picking.type', string='Transferencia interna')

class unispice_location(models.Model):
    _inherit='stock.location'

    def crear_unispice_location(self):
        for r in self:
            ubi=self.env['unispice_lote.location'].search([('location_id','=',r.id)],limit=1)
            if not ubi:
                self.env['unispice_lote.location'].create({'location_id':r.id,'name':'Ingreso:'+r.complete_name})

class unispice_ubicacion(models.Model):
    _name='unispice_lote.location'
    _description='Registrar las ubicaciones y movimientos de lotes'
    _inherit = ['barcodes.barcode_events_mixin']
    name=fields.Char("Nombre")
    location_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion')
    mensaje=fields.Char("Mensaje")
    alternative_ids=fields.One2many(comodel_name='unispice_lote.alternative',inverse_name='unispice_location_id',string='Items')
    alternative_id=fields.Many2one(comodel_name='unispice_lote.alternative',string='LOTE A MOVER')
    multiples_alternatives=fields.Boolean("Multiples alternativas")
    error=fields.Boolean("Error")
    cantidad=fields.Float("Cantidad")
    texto=fields.Text("Texto",compute='get_texto')

    @api.depends('alternative_id')
    def get_texto(self):
        for r in self:
            texto=''
            if r.alternative_id:
                texto=texto+'<table><tr><td colspan="2"><h1>Información del lote</h1></td></tr>'
                texto=texto+'<tr><td>Lote</td><td>'+r.alternative_id.quant_id.lot_id.name+'</td></tr>'
                texto=texto+'<tr><td>Codigo</td><td>'+r.alternative_id.quant_id.product_id.default_code+'</td></tr>'
                texto=texto+'<tr><td>Producto</td><td>'+r.alternative_id.quant_id.product_id.name+'</td></tr>'
                texto=texto+'<tr><td>Cantidad</td><td>'+str(r.alternative_id.quant_id.available_quantity)+'</td></tr>'
                texto=texto+'<tr><td>Unidad</td><td>'+r.alternative_id.quant_id.product_uom_id.name+'</td></tr>'
                texto=texto+'<tr><td>Desde</td><td>'+r.alternative_id.quant_id.location_id.complete_name+'</td></tr>'
                texto=texto+'</table>'
            r.texto=texto

    def on_barcode_scanned(self, barcode):
        lote=self.env['stock.production.lot'].search([('name', '=', barcode)],limit=1)
        #r=self.env['unispice_lote.location'].browse(self.id)
        self.alternative_ids.unlink()
        dic={}
        self.alternative_id=None
        self.multiples_alternatives=False
        self.mensaje=''
        self.error=False       
        if lote:            
            quants=self.env['stock.quant'].search([('lot_id', '=', lote.id),('available_quantity','>',0)])
            if quants:
                x=0
                for q in quants:
                    if q.location_id.usage=='internal':
                        x=x+1
                        alt=self.env['unispice_lote.alternative'].create({'unispice_location_id':self.id,'quant_id':q.id})
                        self.alternative_id=alt.id
                        self.cantidad=q.available_quantity
                if x>1:
                    self.multiples_alternatives=True
                else:
                    if x==1:
                        self.multiples_alternatives=False
                    else:
                        self.mensaje='EL LOTE '+lote.name+' NO TIENE EXISTENCIAS '+ str(lote.id)
                        self.error=True
            else:
                self.mensaje='EL LOTE '+lote.name+' NO TIENE EXISTENCIAS '+str(lote.id)
                self.error=True
        else:
            self.mensaje='LOTE NO REGISTRADO'
            self.error=True

    def procesar(self):
        self.ensure_one()
        if self.alternative_id:
            if self.cantidad==self.alternative_id.quant_id.available_quantity:
                dic={}
                dic['picking_type_id']=self.location_id.company_id.internal_transfer_id.id
                dic['move_type']='one'
                dic['location_dest_id']=self.location_id.id
                dic['location_id']=self.alternative_id.quant_id.location_id.id
                pick=self.env['stock.picking'].create(dic)
                dicl={}
                dicl['company_id']=self.location_id.company_id.id
                dicl['date']=datetime.today()
                dicl['location_dest_id']=self.location_id.id
                dicl['location_id']=self.alternative_id.quant_id.location_id.id
                dicl['name']=pick.name
                dicl['product_id']=self.alternative_id.quant_id.product_id.id
                dicl['product_uom']=self.alternative_id.quant_id.product_uom_id.id
                dicl['product_uom_qty']=self.alternative_id.quant_id.available_quantity
                dicl['picking_id']=pick.id
                self.env['stock.move'].create(dicl)
                pick.action_confirm()
                pick.action_assign()
                for x in pick.move_line_ids_without_package:
                    x.write({'qty_done':x.product_uom_qty})
                pick.button_validate()
                if pick.state=='done':
                    self.mensaje='MOVIMIENTO COMPLETADO'
                    self.alternative_ids.unlink()
                    self.alternative_id=None
                    self.multiples_alternatives=False
                    self.error=False
                    self.env['unispice_lote.log'].create({'picking_id':pick.id,'name':pick.name,'unispice_location_id':self.id})
                else:
                    self.mensaje='ERROR AL REGISTRAR EL MOVIMIENTO'
                    self.error=True
            else:
                self.mensaje='EL MOVIMIENTO NO PUEDE REALIZARSE PORQUE LA CANTIDAD DISPONIBLE HA VARIADO'
                self.error=True





class unispice_ubicacion(models.Model):
    _name='unispice_lote.alternative'
    _description='Registrar las alternativas de movimiento posible'
    name=fields.Char('Alternativa',compute='get_name')
    unispice_location_id=fields.Many2one(comodel_name='unispice_lote.location', string='Ubicacion')
    quant_id=fields.Many2one(comodel_name='stock.quant', string='Quant')
    
    def get_name(self):
        for r in self:
            r.name='Pro.:'+r.quant_id.product_id.default_code+' desde:'+r.quant_id.location_id.name+ '  Cantidad:'+str(r.quant_id.available_quantity)+ ' '+r.quant_id.product_uom_id.name


class unispice_lot_log(models.Model):
    _name='unispice_lote.log'
    _description='Registrar los movimientos '
    name=fields.Char('Movimiento')
    picking_id=fields.Many2one(comodel_name='stock.picking', string='picking')
    unispice_location_id=fields.Many2one(comodel_name='unispice_lote.location', string='Ubicacion')
