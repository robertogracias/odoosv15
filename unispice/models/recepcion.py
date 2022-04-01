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



#Clase para la recepcion de lotes
class unispice_recepcion(models.Model):
    _name='unispice.recepcion'
    _inherit='mail.thread'
    _description='Recepcion'
    _sql_constraints = [
        ('Boleta_Unico', 'unique (name)', 'El Numero de boleta debe ser unico')
    ]
    name=fields.Char('Boleta',copy=False,compute='get_name',store=True)
    serie=fields.Char('Serie')
    numero=fields.Integer('Entero')
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


    #DATOS A CALCULAR SUMANDO LOS LOTES Y PALLETS PARA LA LIQUIDACION
    porcentaje_defectos=fields.Float("% Defectos Calidad")
    porcentaje_rechazo=fields.Float("% Rechazo Maquila")
    peso_empacado=fields.Float("Peso empacado exportacion")
    peso_empacado_green_bean_autorizado=fields.Float("Peso empacado green bean autorizado")
    peso_empacado_local_autorizado=fields.Float("Peso empacado local autorizado")
    peso_empacado_green_bean=fields.Float("Peso empacado green bean")
    peso_empacado_local=fields.Float("Peso empacado local")
    peso_empacado_para_liquidar=fields.Float("Peso empacado para liquidar")
    libras_rechazo_real=fields.Float("Libras Rechazao real")
    porcentaje_rechazo_real=fields.Float("% Rechazo Real")
    porcentaje_rechazo_tolerado=fields.Float("% Rechazo Tolerado")
    libras_a_liquidar_sin_rechazo=fields.Float("Libras a liquidar sin rechazo")
    porcentaje_ajuste=fields.Float("% ajuste")
    libras_a_pagar_ajustadas=fields.Float("Libras a pagar ajustadas")
    libras_de_rechazo_a_aplicar=fields.Float("Libras de rechazo a aplicar")
    porcentaje_rechazo_liquidado=fields.Float("% Rechazo Liquidado")
    precio_compra=fields.Float("Precio de Compra")
    total_a_pagar=fields.Float("Total a pagar")
    liquidacion_id=fields.Many2one(comodel_name='unispice.liquidacion', string='Liquidacion')
    liquidacion_batch_id=fields.Many2one(comodel_name='unispice.liquidacion.batch', string='Liquidacion batch')
    
    
    
    


    @api.depends('serie','numero')
    def get_name(self):
        for r in self:
            texto=''
            separador=''
            if r.serie:
                texto=r.serie
                separador='-'
            if r.numero:
                texto=texto+separador+str(r.numero)
            r.name=texto
        

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
                l.name=r.name+'-'+str(x)
                x=x+1
    
    def confirmar(self):
        for r in self:
            r.renumerar_lineas()
            for l in r.detalle_ids:
                #creando el lote
                dic1={}
                dic1['name']=l.name
                dic1['product_id']=r.producto_id.id
                dic1['boleta_id']=r.id
                dic1['company_id']=r.location_id.company_id.id
                dic1['canastas']=l.canastas
                dic1['tara_canasta']=l.tara_canasta
                dic1['tara_pallet']=l.tara_pallet
                
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
                #dicl={}
                #dicl['company_id']=r.location_id.company_id.id
                #dicl['date']=datetime.today()
                #dicl['location_dest_id']=r.location_id.id
                #dicl['location_id']=r.location_id.company_id.inbound_transfer_id.default_location_src_id.id
                #dicl['name']=l.name
                #dicl['origin']=r.name
                #dicl['product_id']=r.pallet_id.id                
                #dicl['product_uom']=1
                #dicl['product_uom_qty']=1
                #dicl['picking_id']=pick.id
                #self.env['stock.move'].create(dicl)
                pick.action_confirm()
                pick.action_assign()
                for x in pick.move_line_ids_without_package:
                    if x.product_id.tracking=='lot':
                        x.write({'qty_done':x.product_uom_qty,'lot_id':lote.id,'origin':r.name})
                    else:
                        x.write({'qty_done':x.product_uom_qty,'origin':r.name})
                pick.button_validate()
                #actualizando las taras
                lote.write({'canastas':l.canastas,'canasta_id':r.canasta_id.id,'pallet_id':r.pallet_id})
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
    ingreso_id=fields.Many2one(comodel_name='unispice.recepcion', string='Boleta')
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
