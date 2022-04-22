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



#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
###Transformmacion 
class unispice_production_order(models.Model):
    _name='unispice.transformacion'
    _description='Ingreso a las ordenes de produccion'
    _inherit='mail.thread'
    #Nombre se genera a partir de una secuencia
    name=fields.Char('Orden de transformacion')
    #Estado de la transformacion
    state=fields.Selection(selection=[('draft','Borrador'),('Iniciado','Iniciado'),('Finalizado','Finalizado')],string="Estado",default='draft')
    running_state=fields.Selection(selection=[('Nuevo','Nuevo'),('Iniciado','Iniciado'),('Pausado','Pausado'),('Finalizado','Finalizado')],string="Running State",default='Nuevo')
    tipo=fields.Selection(selection=[('mp','Materia Prima'),('pt','Producto Terminado')],string="Tipo",default='mp')
    #Proceso en el que se desarrollara la transformacion
    proceso_id=fields.Many2one(comodel_name='mrp.workcenter', string='Proceso')
    #Producto terminado a producir
    product_id=fields.Many2one(comodel_name='product.product', string='Producto')
    #fecha y hora de inicio
    producto_rechazo_id=fields.Many2one(comodel_name='product.product', string='Producto de rechazo')
    #fecha y hora de inicio
    fecha_start=fields.Datetime("Fecha de Inicio")
    #fecha y hora de finalizacion
    fecha_end=fields.Datetime("Fecha de Finalizacion")    
    
    #Lotes de ingreso
    ingresos_mp_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_mp', string='Ingresos Materia Prima',inverse_name='transformacion_id')
    ingresos_me_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_me', string='Ingresos Material de Empaque',inverse_name='transformacion_id')
    ingresos_pt_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_pt', string='Ingresos Producto Terminado',inverse_name='transformacion_id')


    saldo_mp_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_mp', string='Ingresos Materia Prima',compute='_compute_lines_mp', inverse='_inverse_lines')
    saldo_me_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_me', string='Ingresos Material de Empaque',compute='_compute_lines_me', inverse='_inverse_lines')
    saldo_pt_ids=fields.One2many(comodel_name='unispice.transformacion.ingreso_pt', string='Ingresos Producto Terminado',compute='_compute_lines_pt', inverse='_inverse_lines')


    def _inverse_lines(self):
        """ Little hack to make sure that when you change something on these objects, it gets saved"""
        pass

    @api.depends('ingresos_mp_ids')
    def _compute_lines_mp(self):
        for production in self:
            production.saldo_mp_ids = production.ingresos_mp_ids

    @api.depends('ingresos_me_ids')
    def _compute_lines_me(self):
        for production in self:
            production.saldo_me_ids = production.ingresos_me_ids

    @api.depends('ingresos_pt_ids')
    def _compute_lines_pt(self):
        for production in self:
            production.saldo_pt_ids = production.ingresos_pt_ids


    salidas_mp_ids=fields.One2many(comodel_name='unispice.transformacion.salida_mp', string='Salidas Materia Prima',inverse_name='transformacion_id')
    salidas_pt_ids=fields.One2many(comodel_name='unispice.transformacion.salida_pt', string='Salidas Producto terminado',inverse_name='transformacion_id')
    salidas_re_ids=fields.One2many(comodel_name='unispice.transformacion.salida_re', string='Salidas Rechazo',inverse_name='transformacion_id')
    salidas_ba_ids=fields.One2many(comodel_name='unispice.transformacion.salida_ba', string='Salidas Basura',inverse_name='transformacion_id')



    track_ids=fields.One2many(comodel_name='unispice.transformacion.time_track', string='Tomas de tiempo',inverse_name='transformacion_id')


    rechazo_mp_ids=fields.One2many(comodel_name='unispice.transformacion.salida_rechazo', string='Rechazos Materia Prima',inverse_name='transformacion_id')
    #Orden de produccion asociada al proceso
    production_id=fields.Many2one(comodel_name='mrp.production', string='Proceso de produccion')
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')

    #wharehouse
    almancen_id=fields.Many2one(comodel_name='stock.warehouse',string='Almacen Id')

    razon_pausa_id=fields.Many2one(comodel_name='unispice.transformacion.time_of',string='Razon de Pausa')
    track_id=fields.Many2one(comodel_name='unispice.transformacion.time_track',string='Traza actual')

    

    #enlaces con planificacion
    cantidad_a_producir=fields.Float(string='Cantidad a producir')
    cantidad_prodducida=fields.Float(string='Cantidad producida')
    order_line_id=fields.Many2one(comodel_name='sale.order.line',string='Orden line Id')
    turno_id=fields.Many2one(comodel_name='unispice.linea.turno',string='Turno en el que esta asignado')
    order_id=fields.Many2one(comodel_name='sale.order',string='Orden Id',related='order_line_id.order_id')
    linea_id=fields.Many2one(comodel_name='unispice.linea',string='Linea de Produccion',related='turno_id.linea_id')
    turno_state=fields.Selection(selection=[('abierto','Abierto'),('cerrado','Cerrado')],string="Estado",related='turno_id.state',store=True,default='abierto')
    partner_id=fields.Many2one(comodel_name='res.partner',string='Cliente',related='order_line_id.order_partner_id')


    def _get_quant(self,lot):        
        quant=None
        quants=self.env['stock.quant'].search([('lot_id', '=', lot.id)])
        if quants:
            x=0
            for q in quants:
                if q.location_id.usage=='internal' and q.available_quantity>0:
                    x=x+1
                    quant=q
            if x>1:
                raise UserError('El Lote ha sido divido:'+str(x))
        return quant


    def _crear_orden(self):
        dp={}
        dp['product_id']=self.product_id.id
        dp['company_id']=self.proceso_id.company_id.id
        dp['consumption']='flexible'
        dp['date_planned_start']=datetime.now()            
        dp['picking_type_id']=self.proceso_id.company_id.transform_transfer_id.id
        dp['location_dest_id']=self.proceso_id.location_input_id.id
        dp['location_src_id']=self.proceso_id.location_output_id.id
        dp['product_qty']=self.cantidad_prodducida        
        dp['product_uom_id']=self.product_id.uom_id.id
        produccion=self.env['mrp.production'].create(dp)
        return produccion
    
    def _crear_movimiento_prod(self,produccion,quant,cantidad,src,target):
        dic1={}
        dic1['product_id']=quant.product_id.id
        dic1['location_id']=src.id
        dic1['location_dest_id']=target.id
        dic1['company_id']=src.company_id.id
        dic1['date']=datetime.now()        
        dic1['product_uom']=quant.product_uom_id.id
        if cantidad<=quant.available_quantity:
            dic1['product_uom_qty']=cantidad
        else:
            raise UserError('El lote de materia prima '+ quant.lot_id.name+ ' no tiene la cantidad requerida :'+str(cantidad)+ ' lote posee:'+str(quant.available_quantity))
        dic1['name']=self.name+' - '+quant.lot_id.name
        dic1['raw_material_production_id']=produccion.id
        mov=self.env['stock.move'].create(dic1)
        #creando el detalle del movimiento
        dl={}
        dl['location_id']=src.id
        dl['product_id']=quant.product_id.id
        dl['product_uom_id']=quant.product_uom_id.id
        dl['location_dest_id']=target.id
        dl['lot_id']=quant.lot_id.id
        dl['product_uom_qty']=0
        dl['qty_done']=0
        dl['move_id']=mov.id
        self.env['stock.move.line'].create(dl)
        return mov

    def _crear_lote(self,product,boleta,product_palet,product_canasta,canastas,lote_name,company):
        dic1={}
        dic1['name']=lote_name
        dic1['product_id']=product.id
        dic1['boleta_id']=boleta.id
        dic1['company_id']=company.id
        dic1['canastas']=canastas
        dic1['canasta_id']=product_canasta.id
        dic1['pallet_id']=product_palet.id
        lote=self.env['stock.production.lot'].create(dic1)
        return lote
    
    def _crear_lote_pt(self,product,boleta,lote_name,company):
        dic1={}
        dic1['name']=lote_name
        dic1['product_id']=product.id
        dic1['boleta_id']=boleta.id
        dic1['company_id']=company.id
        lote=self.env['stock.production.lot'].create(dic1)
        return lote


    def _crear_movimiento_sal(self,produccion,product,lote,cantidad,src,target):
        dic1={}
        dic1['product_id']=product.id
        dic1['location_id']=src.id
        dic1['location_dest_id']=target.id
        dic1['company_id']=src.company_id.id
        dic1['date']=datetime.now()
        dic1['product_uom']=product.uom_id.id
        
        dic1['name']=self.name+' - '+lote.name
        dic1['production_id']=produccion.id
        mov=self.env['stock.move'].create(dic1)
        #creando el detalle del movimiento
        dl={}
        dl['location_id']=src.id
        dl['product_id']=product.id
        dl['product_uom_id']=product.uom_id.id
        dl['location_dest_id']=target.id
        dl['lot_id']=lote.id
        dl['product_uom_qty']=0
        dl['qty_done']=cantidad
        dl['move_id']=mov.id
        self.env['stock.move.line'].create(dl)
        return mov

    def ejecutar_transformacion(self):
        for r in self:
            #creando la orden de produccion
            produccion=r._crear_orden()
            r.production_id=produccion.id
            boleta=None

            #Movimientos de materia prima
            for l in r.ingresos_mp_ids:
                quant=r._get_quant(l.lot_id)
                if l.lot_id.boleta_id:
                    boleta=l.lot_id.boleta_id
                cantidad=l.peso_neto_in-l.peso_neto_out
                #movimiento del producto
                mov=r._crear_movimiento_prod(produccion,quant,l.peso_neto_in-l.peso_neto_out,r.proceso_id.location_input_id,r.proceso_id.location_factory_id)
                l.move_id=mov.id
            #Movimientos de material de empaque
            for l in r.ingresos_me_ids:
                quant=r._get_quant(l.lot_id)
                if l.lot_id.boleta_id:
                    boleta=l.lot_id.boleta_id
                #movimiento del producto
                mov=r._crear_movimiento_prod(produccion,quant,l.cantidad-l.cantidad_out,r.proceso_id.location_input_id,r.proceso_id.location_factory_id)
                l.move_id=mov.id
            for l in r.ingresos_pt_ids:
                quant=r._get_quant(l.lot_id)
                if l.lot_id.boleta_id:
                    boleta=l.lot_id.boleta_id
                cantidad=l.unidades_in-l.unidades_out
                #movimiento del producto
                mov=r._crear_movimiento_prod(produccion,quant,cantidad,r.proceso_id.location_input_id,r.proceso_id.location_factory_id)
                l.move_id=mov.id
            
            correlativo=0
            for l in r.salidas_mp_ids:
                correlativo=correlativo+1
                lote=r._crear_lote(l.product_id,boleta,l.pallet_id,l.canasta_id,l.canastas_out,(boleta.name if boleta else '')+'-'+r.name+'-'+str(correlativo),r.proceso_id.company_id)
                mov=r._crear_movimiento_sal(produccion,l.product_id,lote,l.peso_neto_out,r.proceso_id.location_factory_id,r.proceso_id.location_output_id)
                l.move_id=mov.id
            for l in r.salidas_re_ids:
                correlativo=correlativo+1
                lote=r._crear_lote(l.product_id,boleta,l.pallet_id,l.canasta_id,l.canastas_out,(boleta.name if boleta else '')+'-'+r.name+'-'+str(correlativo),r.proceso_id.company_id)
                mov=r._crear_movimiento_sal(produccion,l.product_id,lote,l.peso_neto_out,r.proceso_id.location_factory_id,r.proceso_id.location_output_id)
                l.move_id=mov.id
            for l in r.salidas_ba_ids:
                correlativo=correlativo+1
                lote=r._crear_lote(l.product_id,boleta,l.pallet_id,l.canasta_id,l.canastas_out,(boleta.name if boleta else '')+'-'+r.name+'-'+str(correlativo),r.proceso_id.company_id)
                mov=r._crear_movimiento_sal(produccion,l.product_id,lote,l.peso_neto_out,r.proceso_id.location_factory_id,r.proceso_id.location_output_id)
                l.move_id=mov.id
            for l in r.salidas_pt_ids:
                correlativo=correlativo+1
                lote=r._crear_lote(l.product_id,boleta,(boleta.name if boleta else '')+'-'+r.name+'-'+str(correlativo),r.proceso_id.company_id)
                mov=r._crear_movimiento_sal(produccion,l.product_id,lote,l.unidades_out,r.proceso_id.location_factory_id,r.proceso_id.location_output_id)
                l.move_id=mov.id
            produccion.action_confirm()

            #produccion.action_toggle_is_locked()
            #produccion.action_assign()
            #for m in produccion.move_raw_ids:
            #    if m.reserved_availability==0:
            #        raise UserError('El Material no esta disponible')
            for m in produccion.move_raw_ids:
                if m.move_line_ids:
                    for l in m.move_line_ids:
                        l.qty_done=l.move_id.product_uom_qty
            produccion.qty_producing=self.cantidad_prodducida
            produccion.button_mark_done()
            r.state='Finalizado'




    def iniciar(self):
        for r in self:
            if not r.track_id:
                dic={}
                dic['inicio']=datetime.now()
                dic['transformacion_id']=r.id
                track=self.env['unispice.transformacion.time_track'].create(dic)
                r.track_id=track.id
                r.running_state='Iniciado'
    
    def detener(self):
        for r in self:
            if r.track_id:
                r.track_id.write({'fin':datetime.now()})
            if not r.razon_pausa_id:
                raise UserError('Debe esepcificarse una razon')
            dic={}
            dic['inicio']=datetime.now()
            dic['transformacion_id']=r.id
            dic['time_of_id']=r.razon_pausa_id.id
            track=self.env['unispice.transformacion.time_track'].create(dic)
            r.razon_pausa_id=None
            r.track_id=track.id
            r.running_state='Pausado'
    
    def reiniciar(self):
        for r in self:
            if r.track_id:
                r.track_id.write({'fin':datetime.now()})
            dic={}
            dic['inicio']=datetime.now()
            dic['transformacion_id']=r.id
            track=self.env['unispice.transformacion.time_track'].create(dic)
            r.track_id=track.id
            r.running_state='Iniciado'

    
    def finalizar(self):
        for r in self:
            if r.track_id:
                r.track_id.write({'fin':datetime.now()})
                r.running_state='Finalizado'



    @api.model
    def create(self, vals):
        vals['name']=self.env['ir.sequence'].next_by_code('unispice.transformacion')
        res = super(unispice_production_order, self).create(vals)
        return res
    

   


#################################################################################################################################################
#Linea de ingreso de material de empaque
class unispice_production_line_ingreso_me(models.Model):
    _name='unispice.transformacion.ingreso_me'
    _description='Ingreso a las ordenes de produccion'    
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    name=fields.Char(string='Ingreso MP',related='lot_id.name')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',related='lot_id.product_id',store=True)
    ##Datos de ingreso
    cantidad=fields.Float(string='Cantidad ')
    cantidad_out=fields.Float(string='Saldo ')
    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')
    move_id=fields.Many2one(comodel_name='stock.move', string='movimiento')

    def get_name(self):
        for r in self:
            r.name=r.lot_id.name+' - '+r.lot_id.product_id.name



  

#Linea de ingreso de materia prima
class unispice_production_line_ingreso_mp(models.Model):
    _name='unispice.transformacion.ingreso_mp'
    _description='Ingreso a las ordenes de produccion'    
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    name=fields.Char(string='Ingreso MP',compute='get_name')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',related='lot_id.product_id',store=True)
    tara_canasta=fields.Float('Tara canasta',related='lot_id.tara_canasta',store=True)
    tara_pallet=fields.Float('Tara Palet',related='lot_id.tara_pallet',store=True)
    ##Datos de ingreso
    canastas_in=fields.Integer('Canastas',compute='get_pesos',store=True)
    peso_bruto_in=fields.Float('Peso Bruto',compute='get_pesos')
    peso_neto_in=fields.Float('Peso neto',compute='get_pesos')
    
    ##Datos de salida
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    canastas_out=fields.Integer('Canastas de salida')
    peso_bruto_out=fields.Float('Peso de retorno')
    peso_neto_out=fields.Float('Peso neto',compute='get_pesos_salida')
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')
    move_id=fields.Many2one(comodel_name='stock.move', string='movimiento')

    #picking de las canastas
    picking_canasta_in_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_out_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')

    def get_name(self):
        for r in self:
            r.name=r.lot_id.name+' - '+r.lot_id.product_id.name


    @api.onchange('lot_id')
    def get_pesos(self):
        for r in self:
            r.canastas_in=r.lot_id.canastas
            r.peso_neto_in=r.lot_id.product_qty
            r.peso_bruto_in=r.lot_id.product_qty+(r.lot_id.canastas*r.tara_canasta)+r.tara_pallet
    
    @api.onchange('peso_bruto_out','canastas_out')
    def get_pesos_salida(self):
        for r in self:
            r.peso_neto_out=r.peso_bruto_out-(r.canastas_out*r.tara_canasta)-r.tara_pallet


    #Linea de ingreso de materia prima
class unispice_production_line_ingreso(models.Model):
    _name='unispice.transformacion.ingreso_pt'
    _description='Ingreso a las ordenes de produccion'    
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    name=fields.Char(string='Ingreso MP',compute='get_name')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',related='lot_id.product_id',store=True)
    tara_canasta=fields.Float('Tara canasta',related='lot_id.tara_canasta',store=True)
    tara_pallet=fields.Float('Tara Palet',related='lot_id.tara_pallet',store=True)
    ##Datos de ingreso
    unidades_in=fields.Float('Cantidad que entra')
    
    ##Datos de salida
    unidades_out=fields.Float('Cantidad que sale')

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    #picking de las canastas
    picking_canasta_in_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_out_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')

    def get_name(self):
        for r in self:
            r.name=r.lot_id.name+' - '+r.lot_id.product_id.name

   


#################################################################################################################################################
#Linea de salida de materia prima
class unispice_production_line_salida_mp(models.Model):
    _name='unispice.transformacion.salida_mp'
    _description='salida a las ordenes de produccion'
    #El lote se generara
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',store=True)
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    tara_pallet=fields.Float('Tara Palet',related='pallet_id.tara',store=True)
    
    ##Datos de salida
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    canastas_out=fields.Integer('Canastas de salida')
    peso_bruto_out=fields.Float('Peso de retorno')
    peso_neto_out=fields.Float('Peso neto',compute='get_pesos_salida')
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')

    #picking de las canastas
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    @api.onchange('peso_bruto_out','canastas_out','bascula_id','canasta_id')
    def get_pesos_salida(self):
        for r in self:
            r.peso_neto_out=r.peso_bruto_out-(r.canastas_out*r.tara_canasta)-r.tara_pallet


#################################################################################################################################################
#Linea de salida de materia prima
class unispice_production_line_salida_re(models.Model):
    _name='unispice.transformacion.salida_re'
    _description='salida a las ordenes de produccion Rechazo'
    #El lote se generara
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',store=True)
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    tara_pallet=fields.Float('Tara Palet',related='pallet_id.tara',store=True)
    
    ##Datos de salida
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    canastas_out=fields.Integer('Canastas de salida')
    peso_bruto_out=fields.Float('Peso de retorno')
    peso_neto_out=fields.Float('Peso neto',compute='get_pesos_salida')
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')

    #picking de las canastas
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    @api.onchange('peso_bruto_out','canastas_out','bascula_id','canasta_id')
    def get_pesos_salida(self):
        for r in self:
            r.peso_neto_out=r.peso_bruto_out-(r.canastas_out*r.tara_canasta)-r.tara_pallet

class unispice_production_line_salida_ba(models.Model):
    _name='unispice.transformacion.salida_ba'
    _description='salida a las ordenes de produccion Basura'
    #El lote se generara
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',store=True)
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    tara_pallet=fields.Float('Tara Palet',related='pallet_id.tara',store=True)
    
    ##Datos de salida
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    canastas_out=fields.Integer('Canastas de salida')
    peso_bruto_out=fields.Float('Peso de retorno')
    peso_neto_out=fields.Float('Peso neto',compute='get_pesos_salida')
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')

    #picking de las canastas
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    @api.onchange('peso_bruto_out','canastas_out','bascula_id','canasta_id')
    def get_pesos_salida(self):
        for r in self:
            r.peso_neto_out=r.peso_bruto_out-(r.canastas_out*r.tara_canasta)-r.tara_pallet


class unispice_production_line_salida_pt(models.Model):
    _name='unispice.transformacion.salida_pt'
    _description='salida a las ordenes de produccion'
    #El lote se generara
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',store=True)
    #canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    #pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    #tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    #tara_pallet=fields.Float('Tara Palet',related='pallet_id.tara',store=True)
    
    ##Datos de salida

    #bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')
    #canastas_out=fields.Integer('Canastas de salida')
    #peso_bruto_out=fields.Float('Peso de retorno')
    #peso_neto_out=fields.Float('Peso neto',compute='get_pesos_salida')
    ##Datos de salida
    unidades_out=fields.Float('Cantidad que sale')

    @api.onchange('peso_bruto_out','canastas_out','bascula_id','canasta_id')
    def get_pesos_salida(self):
        for r in self:
            r.peso_neto_out=r.peso_bruto_out-(r.canastas_out*r.tara_canasta)-r.tara_pallet
    

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    #picking de las canastas
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')


#################################################################################################################################################
#Linea de salida de materia prima
class unispice_production_line_rechazo(models.Model):
    _name='unispice.transformacion.salida_rechazo'
    _description='salida a las ordenes de produccion'
    #El lote se generara
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string='Lote')
    product_id=fields.Many2one(comodel_name='product.product', string='Producto',store=True)
    canasta_id=fields.Many2one(comodel_name='product.product', string='Tipo Canasta',domain='[("is_canasta","=",True)]')
    pallet_id=fields.Many2one(comodel_name='product.product', string='Tipo Pallet',domain='[("is_pallet","=",True)]')
    tara_canasta=fields.Float('Tara canasta',related='canasta_id.tara',store=True)
    tara_pallet=fields.Float('Tara Palet',related='pallet_id.tara',store=True)
    
    ##Datos de salida
    canastas_out=fields.Integer('Canastas de salida')
    peso_bruto_out=fields.Float('Peso de retorno')
    peso_neto_in=fields.Float('Peso neto',compute='get_pesos_salida')
    bascula_id=fields.Many2one(comodel_name='basculas.bascula', string='Bascula')

    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')
    move_id=fields.Many2one(comodel_name='stoc.move', string='movimiento')

    #picking de las canastas
    picking_id=fields.Many2one(comodel_name='stock.picking', string='Entrada de las canastas')
    picking_canasta_id=fields.Many2one(comodel_name='stock.picking', string='Retorno de las canastas')


class unispice_production_time_off(models.Model):
    _name='unispice.transformacion.time_of'
    _description='Razones de tiempo muerto'
    name=fields.Char("razon de tiempo muerto")


class unispice_production_time_track(models.Model):
    _name='unispice.transformacion.time_track'
    _description='Toma de tiempo'
    name=fields.Char(string='Nombre')
    inicio=fields.Datetime(string='Inicio')
    fin=fields.Datetime(string='Fin')
    duracion=fields.Float(string='Duracion',compute='get_duracion')
    time_of_id=fields.Many2one(comodel_name='unispice.transformacion.time_of', string='Tiempo fuera')
    transformacion_id=fields.Many2one(comodel_name='unispice.transformacion', string='Transformacion')
    turno_id=fields.Many2one(comodel_name='unispice.linea.turno',string='Turno en el que esta asignado',related='transformacion_id.turno_id')
    linea_id=linea_id=fields.Many2one(comodel_name='unispice.linea',string='Linea de Produccion',related='transformacion_id.linea_id')

    @api.depends('inicio','fin')
    def get_duracion(self):
        for r in self:
            if r.inicio and r.fin:
                datediff=r.fin-r.inicio
                r.duracion=datediff.total_seconds()/3600
            else:
                r.duracion=0.0
