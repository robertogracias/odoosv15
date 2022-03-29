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



###################################################################################################################################################333
####Clases para la solicitud de materias primas
class unispice_solicitud(models.Model):
    _name='unispice.solicitud'
    _inherit='mail.thread'
    _description='Permite realizar las solicitudes materia prima'
    name=fields.Char('Solicitud de Materia Prima',default="/")
    note=fields.Char("Notas",tracking=True)
    state=fields.Selection(selection=[('draft','Borrador'),('Solicitado','Entrada'),('Cerrado','Cerrado')],string="Estado",default='draft',tracking=True)
    pallet_ids=fields.One2many(comodel_name='unispice.solicitud.pallet', string='Pallets',inverse_name='solicitud_id')
    fecha_solicitud=fields.Date("Fecha de Entrada",tracking=True)
    pallet_id=fields.Many2one(comodel_name='stock.production.lot', string='Pallet a Agregar',domain='[("liquidado","=",False)]')

    @api.model
    def create(self, vals):
        vals['name']=self.env['ir.sequence'].next_by_code('unispice.sol')
        res = super(unispice_solicitud, self).create(vals)
        return res

    #cambia el estado a solicitado
    def solicitar(self):
        for r in self:
            r.state='Solicitado'
            r.fecha_solicitud=datetime.now()
            
            for l in r.pallet_ids:
                l.state='Solicitado'

    #Cierra los 
    def cerrar(self):
        for r in self:
            r.state='Cerrado'
            for l in r.pallet_ids:
                if l.state!='Entregado':
                    l.state='Cancelado'

    def addline(self):
        for r in self:
            if r.pallet_id:
                lote=self.env['stock.production.lot'].search([('name', '=', r.pallet_id.name)],limit=1)
                quant=None
                if lote:
                    #validando pallet
                    anterior=self.env['unispice.solicitud.pallet'].search([('lot_id','=',lote.id),('state','!=','Cancelado')],limit=1)
                    if anterior:
                        raise UserError('El pallet ya esta en otra solicitud')
                    #validando cantidades            
                    quants=self.env['stock.quant'].search([('lot_id', '=', lote.id),('available_quantity','>',0)])
                    if quants:
                        x=0
                        for q in quants:
                            if q.location_id.usage=='internal':
                                x=x+1
                        if x>1:
                            raise UserError('EL LOTE HA SIDO DIVIDIDO')
                        else:
                            if x==1:
                                quant=q
                            else:
                                raise UserError('EL LOTE NO TIENE EXISTENCIAS')
                    else:
                        raise UserError('EL LOTE NO TIENE EXISTENCIAS')
                else:
                    raise UserError('EL LOTE NO ESTA REGISTRADO')
                dic={}
                dic['lot_id']=lote.id
                dic['solicitud_id']=r.id
                dic['state']='draft'
                dic['location_src_id']=quant.location_id.id
                dic['boleta_id']=lote.boleta_id.id
                dic['canastas']=lote.canastas
                dic['peso_bruto']=quant.available_quantity+(lote.tara_canasta*lote.canastas)+lote.tara_pallet
                dic['tara_canasta']=lote.tara_canasta
                dic['tara_pallet']=lote.tara_pallet
                dic['peso_neto']=quant.available_quantity

                self.env['unispice.solicitud.pallet'].create(dic)
     


#palet solicitada
class unispice_solicitud_detail(models.Model):
    _name='unispice.solicitud.pallet'
    _description='Pallet solicitada'

    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    state=fields.Selection(selection=[('draft','Borrador'),('Solicitado','Solicitado'),('Entregado','Entregado'),('Cancelado','Cancelado')],string="Estado",default='draft')
    solicitud_id=fields.Many2one(comodel_name='unispice.solicitud', string='Solicutd')
    location_src_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion')
    ubicado=fields.Boolean("Localizado")

    #atributos que se registran al cambiar el lote
    boleta_id=fields.Many2one(comodel_name='unispice.recepcion', string='Boleta')
    product_id=fields.Many2one(comodel_name='product.product',related='lot_id.product_id' ,string='Producto')
    cantidad=fields.Float('Cantidad')
    canastas=fields.Integer("Canastas")
    peso_bruto=fields.Float("Peso bruto")
    tara_canasta=fields.Float('Tara canasta',related='lot_id.tara_canasta',store=True)
    tara_pallet=fields.Float('Tara Palet',related='lot_id.tara_pallet',store=True)
    peso_neto=fields.Float('Peso neto',store=True)

    #atributos para el movimiento
    peso_obtenido=fields.Float("Peso Obtenido")
    canastas_transferir=fields.Integer("Canastas a transferir")
    location_dest_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion de destino')
    peso_neto_transferir=fields.Float("Peso neto a transferir",compute='get_peso_neto')
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')

    @api.depends('peso_obtenido','canastas_transferir')
    def get_peso_neto(self):
        for r in self:
            r.peso_neto_transferir=r.peso_obtenido-(r.tara_canasta*r.canastas_transferir)-r.tara_pallet


    def cancelar(self):
        for r in self:
            r.state='Cancelado'


    def get_from_bascula(self):
        for r in self:
            r.bascula_id.leer()
            peso=r.bascula_id.ultima_lectura
            r.peso_obtenido=peso


    #movimientos del traslado.
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Movimiento de producto')
    ajuste_id=fields.Many2one(comodel_name='stock.inventory', string='Ajuste de Inventario')

    def entregar(self):
        for r in self:
            ##crear movimiento de producto
            
            ##Creando Ajuste
            dicA={}
            dicA['name']='Ajuste '+r.lot_id.name
            dicA['location_ids']=[(6,0,[r.location_src_id.id])]
            dicA['product_ids']=[(6,0,[r.lot_id.product_id.id,r.lot_id.canasta_id.id])]
            dicA['prefill_counted_quantity']='counted'
            ajuste=self.env['stock.inventory'].create(dicA)
            ajuste.action_start()
            
            for l in ajuste.line_ids:
                if l.prod_lot_id.id==r.lot_id.id:
                    l.product_qty=r.peso_neto_transferir
                if l.product_id.id==r.lot_id.canasta_id.id:
                    l.product_qty=l.product_qty+(r.canastas-r.canastas_transferir)
            ajuste.action_validate()
            r.ajuste_id=ajuste.id


            #creando el picking
            dic={}
            dic['picking_type_id']=r.location_dest_id.company_id.inbound_transfer_id.id
            dic['move_type']='one'
            dic['origin']='Solicitud MP'+r.solicitud_id.name
            dic['location_dest_id']=r.location_dest_id.id
            dic['location_id']=r.location_src_id.id
            pick=self.env['stock.picking'].create(dic)
            #creando la linea de producto
            dicl={}
            dicl['company_id']=r.location_dest_id.company_id.id
            dicl['date']=datetime.today()
            dicl['location_dest_id']=r.location_dest_id.id
            dicl['location_id']=r.location_src_id.id
            dicl['name']=r.lot_id.product_id.name+' '+r.lot_id.name
            dicl['origin']='Solicitud MP'+r.solicitud_id.name
            dicl['product_id']=r.lot_id.product_id.id                
            dicl['product_uom']=r.lot_id.product_id.uom_id.id
            dicl['product_uom_qty']=r.peso_neto_transferir
            dicl['picking_id']=pick.id
            self.env['stock.move'].create(dicl)
            #creando la linea de las canastas
            dicl={}
            dicl['company_id']=r.location_dest_id.company_id.id
            dicl['date']=datetime.today()
            dicl['location_dest_id']=r.location_dest_id.id
            dicl['location_id']=r.location_src_id.id
            dicl['name']='Canastas '+r.lot_id.name
            dicl['origin']='Solicitud MP'+r.solicitud_id.name
            dicl['product_id']=r.lot_id.canasta_id.id                
            dicl['product_uom']=1
            dicl['product_uom_qty']=r.canastas_transferir
            dicl['picking_id']=pick.id
            self.env['stock.move'].create(dicl)
            pick.action_confirm()
            pick.action_assign()
            for x in pick.move_line_ids_without_package:
                if x.product_id.tracking=='lot':
                    x.write({'qty_done':x.product_uom_qty,'lot_id':r.lot_id.id,'origin':'Solicitud MP'+r.solicitud_id.name})
                else:
                    x.write({'qty_done':x.product_uom_qty,'origin':'Solicitud MP'+r.solicitud_id.name})
            pick.button_validate()
            r.state='Entregado'
            r.picking_id=pick.id



    def open_form(self):
        for r in self:
            compose_form = self.env.ref('unispice.unispice_solicitud_linea_form', False)
            ctx = dict(
            )
            return {
                'name': 'Transferencia de Pallet',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'unispice.solicitud.pallet',
                'res_id': r.id,
                'views': [(compose_form.id, 'form')],
                'target': 'new',
                'view_id': 'compose_form.id',
                'flags': {'action_buttons': True},
                'context': ctx
            }

    