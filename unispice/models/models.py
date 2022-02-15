# -*- coding: utf-8 -*-


from ast import Store
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
    inbound_transfer_id=fields.Many2one(comodel_name='stock.picking.type', string='Transferencia de ingreso')

class unispice_location(models.Model):
    _inherit='stock.location'

    def crear_unispice_location(self):
        for r in self:
            ubi=self.env['unispice.location'].search([('location_id','=',r.id)],limit=1)
            if not ubi:
                self.env['unispice.location'].create({'location_id':r.id,'name':'Ingreso:'+r.complete_name})

class unispice_ubicacion(models.Model):
    _name='unispice.location'
    _description='Registrar las ubicaciones y movimientos de lotes'
    _inherit = ['barcodes.barcode_events_mixin']
    name=fields.Char("Nombre")
    location_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion')
    mensaje=fields.Char("Mensaje")
    alternative_ids=fields.One2many(comodel_name='unispice.alternative',inverse_name='unispice_location_id',string='Items')
    alternative_id=fields.Many2one(comodel_name='unispice.alternative',string='LOTE A MOVER')
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
                        alt=self.env['unispice.alternative'].create({'unispice_location_id':self.id,'quant_id':q.id})
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
                    self.env['unispice.log'].create({'picking_id':pick.id,'name':pick.name,'unispice_location_id':self.id})
                else:
                    self.mensaje='ERROR AL REGISTRAR EL MOVIMIENTO'
                    self.error=True
            else:
                self.mensaje='EL MOVIMIENTO NO PUEDE REALIZARSE PORQUE LA CANTIDAD DISPONIBLE HA VARIADO'
                self.error=True





class unispice_ubicacion(models.Model):
    _name='unispice.alternative'
    _description='Registrar las alternativas de movimiento posible'
    name=fields.Char('Alternativa',compute='get_name')
    unispice_location_id=fields.Many2one(comodel_name='unispice.location', string='Ubicacion')
    quant_id=fields.Many2one(comodel_name='stock.quant', string='Quant')
    
    def get_name(self):
        for r in self:
            r.name='Pro.:'+r.quant_id.product_id.default_code+' desde:'+r.quant_id.location_id.name+ '  Cantidad:'+str(r.quant_id.available_quantity)+ ' '+r.quant_id.product_uom_id.name


class unispice_lot_log(models.Model):
    _name='unispice.log'
    _description='Registrar los movimientos '
    name=fields.Char('Movimiento')
    picking_id=fields.Many2one(comodel_name='stock.picking', string='picking')
    unispice_location_id=fields.Many2one(comodel_name='unispice.location', string='Ubicacion')


class unispice_product(models.Model):
    _inherit='product.template'
    is_canasta=fields.Boolean('Es Canasta')
    is_pallet=fields.Boolean('Es Pallet')
    tara=fields.Float('Tara')


class unispice_recepcion(models.Model):
    _name='unispice.recepcion'
    _description='Recepcion'
    _sql_constraints = [
        ('Boleta_Unico', 'unique (name)', 'El Numero de boleta debe ser unico')
    ]
    name=fields.Char('Boleta',copy=False)
    fecha_ingreso=fields.Datetime("Fecha y hora de ingreso")
    proveedor_id=fields.Many2one(comodel_name='res.partner', string='Proveedor')
    producto_id=fields.Many2one(comodel_name='product.product', string='Producto')
    fecha_cosecha=fields.Date('Fecha de cosecha')
    etapa=fields.Char('Etapa')
    viaje_id=fields.Char('Id del viaje')
    peso_campo=fields.Float('Peso campo')
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    tara_pallet=fields.Float('Tara pallet',related='pallet_id.tara',store=True)
    notas=fields.Text("Notas")

    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    detalle_ids=fields.One2many(comodel_name='unispice.recepcion.line',inverse_name='ingreso_id',string='Pallets')
    state=fields.Selection(selection=[('draft','Borrador'),('done','Confirmado'),('cancel','Cancelado')],string="Estado",default='draft')
    location_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion de llegada')
    label_id=fields.Many2one(comodel_name='etiquetas.label', string='Etiqueta')

    def agregar_linea(self):
        for r in self:
            r.bascula_id.leer()
            peso=r.bascula_id.ultima_lectura
            dic={}
            dic['ingreso_id']=r.id
            dic['peso_bruto']=peso
            self.env['unispice.recepcion.line'].create(dic)
            r.renumerar_lineas()

    def renumerar_lineas(self):
        for r in self:
            x=1
            for l in r.detalle_ids:
                l.name='CA-'+r.name+'-'+str(x)
                x=x+1
    
    def confirmar(self):
        for r in self:
            r.renumerar_lineas()
            for l in r.detalle_ids:
                #creando el lote
                dic1={}
                dic1['name']=l.name
                dic1['product_id']=r.producto_id.id
                dic1['company_id']=r.location_id.company_id.id
                lote=self.env['stock.production.lot'].create(dic1)
                #creando el picking
                dic={}
                dic['picking_type_id']=r.location_id.company_id.inbound_transfer_id.id
                dic['move_type']='one'
                dic['origin']=r.name
                dic['location_dest_id']=r.location_id.id
                dic['location_id']=r.location_id.company_id.inbound_transfer_id.default_location_src_id.id
                pick=self.env['stock.picking'].create(dic)
                #creando la linea de producto
                dicl={}
                dicl['company_id']=r.location_id.company_id.id
                dicl['date']=datetime.today()
                dicl['location_dest_id']=r.location_id.id
                dicl['location_id']=r.location_id.company_id.inbound_transfer_id.default_location_src_id.id
                dicl['name']=l.name
                dicl['origin']=r.name
                dicl['product_id']=r.producto_id.id                
                dicl['product_uom']=r.producto_id.uom_id.id
                dicl['product_uom_qty']=l.peso_neto
                dicl['picking_id']=pick.id
                self.env['stock.move'].create(dicl)
                #creando la linea de las canastas
                dicl={}
                dicl['company_id']=r.location_id.company_id.id
                dicl['date']=datetime.today()
                dicl['location_dest_id']=r.location_id.id
                dicl['location_id']=r.location_id.company_id.inbound_transfer_id.default_location_src_id.id
                dicl['name']=l.name
                dicl['origin']=r.name
                dicl['product_id']=r.canasta_id.id                
                dicl['product_uom']=1
                dicl['product_uom_qty']=l.canastas
                dicl['picking_id']=pick.id
                self.env['stock.move'].create(dicl)
                #creando la linea del palet
                dicl={}
                dicl['company_id']=r.location_id.company_id.id
                dicl['date']=datetime.today()
                dicl['location_dest_id']=r.location_id.id
                dicl['location_id']=r.location_id.company_id.inbound_transfer_id.default_location_src_id.id
                dicl['name']=l.name
                dicl['origin']=r.name
                dicl['product_id']=r.pallet_id.id                
                dicl['product_uom']=1
                dicl['product_uom_qty']=1
                dicl['picking_id']=pick.id
                self.env['stock.move'].create(dicl)
                pick.action_confirm()
                pick.action_assign()
                for x in pick.move_line_ids_without_package:
                    if x.product_id.tracking=='lot':
                        x.write({'qty_done':x.product_uom_qty,'lot_id':lote.id,'origin':r.name})
                    else:
                        x.write({'qty_done':x.product_uom_qty,'origin':r.name})
                pick.button_validate()
                #ejecutando las etiquetas
                dice={}
                dice['name']=r.name+'-'+r.producto_id.name
                dice['quantity']=1
                dice['counter']=0
                dice['tipo']=r.label_id.tipo
                dice['content']=r.label_id.evaluate(r.producto_id,lote,r.location_id.company_id)
                label=self.env['etiquetas.run.item'].create(dice)
                l.etiqueta_id=label.id
                l.picking_id=pick.id
            r.state='done'



class unispice_reception_line(models.Model):
    _name='unispice.recepcion.line'
    _description='Linea de recepcion'
    name=fields.Char('Codigo Pallet')
    ingreso_id=fields.Many2one(comodel_name='unispice.recepcion', string='Proveedor')
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Transferencia')
    temperatura=fields.Float("Temperatura")
    canastas=fields.Integer("Canastas")
    peso_bruto=fields.Float("Peso bruto")
    tara_canasta=fields.Float('Tara canasta',related='ingreso_id.tara_canasta',store=True)
    tara_pallet=fields.Float('Tara Palet',related='ingreso_id.tara_pallet',store=True)
    peso_neto=fields.Float('Peso neto',compute='get_peso_neto',store=True)
    etiqueta_id=fields.Many2one(comodel_name='etiquetas.run.item', string='Etiqueta')

    @api.depends('ingreso_id','tara_canasta','peso_bruto','tara_pallet','canastas')
    def get_peso_neto(self):
        for r in self:
            r.peso_neto=r.peso_bruto-(r.canastas*r.tara_canasta)-r.tara_pallet

   
    def imprimir(self):
        self.ensure_one()
        compose_form = self.env.ref('etiquetas.labelrun_item_form', False)
        ctx = dict(
        )
        return {
            'name': 'Imprimir',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'etiquetas.run.item',
            'res_id': self.etiqueta_id.id,
            'views': [(compose_form.id, 'form')],
            'target': 'new',
            'view_id': 'compose_form.id',
            'flags': {'action_buttons': False},
            'context': ctx
        }

    

