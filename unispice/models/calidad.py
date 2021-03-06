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


##########################################################################################################################################################
##Configuracion
class unispice_tipoproducto(models.Model):
    _name='unispice.tipo_producto'
    _description='Tipo de Producto'
    name=fields.Char('Tipo de Producto')
    


class unispice_configuration(models.Model):
    _name='unispice.configuration'
    _description='Configuracion de almacenes'
    name=fields.Char('Nombre')
    partner_id=fields.Many2one(comodel_name='res.partner', string='Sociedad',domain='[("unispice_sociedad","=",True)]')
    almacen_id=fields.Many2one(comodel_name='integrador_sap_unispice.warehouse', string='Almacen')
    taxcode_id=fields.Many2one(comodel_name='integrador_sap_unispice.tax_code', string='Tax Code')



class unispice_qualitycheck(models.Model):
    _name='unispice.quatily_item'
    _description='Item del control de calidad'
    name=fields.Char('Punto a revisar')
    porcentaje_min=fields.Float("Porcentaje minimo")
    porcentaje_max=fields.Float("Porcentaje maximo")
    tipo=fields.Selection(selection=[('Materia Prima','Materia Prima'),('Producto','Producto'),('Proceso','Proceso')],string='Tipo')
    categoria_id=fields.Many2one(comodel_name='product.category', string='Categoria de productos')
    proceso_id=fields.Many2one(comodel_name='mrp.workcenter', string='Proceso')



   


class unispice_check_item(models.Model):
    _name='unispice.quatily_check_item'
    _description='Item del control de calidad'
    _inherit=['image.mixin']
    name=fields.Char('Punto a revisar')
    
    aprobado=fields.Boolean("Aprobado")
    item_id=fields.Many2one(comodel_name='unispice.quatily_item', string='item de calidad')
    check_id=fields.Many2one(comodel_name='quality.check', string='Control')
    muestra_afectada=fields.Float("Muestra afectada")
    porcentaje=fields.Float(string="Porcentaje aplicado",compute='compute_percentaje')
    proyectado=fields.Float(string="Cantidad proyectada",compute='compute_percentaje')
    rango=fields.Char(string='Rango valido',compute='compute_percentaje')
    #imagen=fields.Binary(string='imagen',attachment=True)

    @api.depends('check_id','muestra_afectada')
    def compute_percentaje(self):
        for r in self:
            r.rango=str(r.item_id.porcentaje_min)+'% - '+str(r.item_id.porcentaje_max)+'%'
            if r.check_id.muestra>0:
                r.porcentaje=(r.muestra_afectada/r.check_id.muestra)*100.00
                if r.check_id.lot_id or r.check_id.boleta_id:
                    r.proyectado=r.check_id.lote_total*(r.muestra_afectada/r.check_id.muestra)
                else:
                    r.proyectado=0.0
                if r.porcentaje>=r.item_id.porcentaje_min and r.porcentaje<=r.item_id.porcentaje_max:
                    r.aprobado=True
                else:
                    r.aprobado=False
            else:
                r.porcentaje=0
                r.proyectado=0
                r.aprobado=False




class unispice_quality_check(models.Model):
    _inherit='quality.check'
    quality_ids=fields.One2many(comodel_name='unispice.quatily_check_item',inverse_name='check_id',string='Items de Calidad')
    muestra=fields.Float("Peso en lbs. de la muestra")
    uom_id=fields.Many2one(comodel_name='uom.uom',string='Unidad de medida',related='product_id.uom_id')
    lote_total=fields.Float(string='Total del lote',compute='calcular_totales')
    porcentaje=fields.Float("Porcentaje total afectada",compute="calcular_totales")
    total_afectado=fields.Float("Total afectado",compute="calcular_totales")
    boleta_id=fields.Many2one(comodel_name='unispice.recepcion',string='Boleta')

    @api.model
    def create(self, vals):
        res = super(unispice_quality_check, self).create(vals)
        if 'boleta_id' in vals:
            boleta=self.env['unispice.recepcion'].browse(vals['boleta_id'])
            if boleta:
                if boleta.quality_check_id:
                    raise UserError('La boleta ya tiene un control de calidad asociado')
                else:
                    boleta.quality_check_id=res.id
                    
        return res

    def write(self, vals):
        if 'boleta_id' in vals:
            boleta=self.env['unispice.recepcion'].browse(vals['boleta_id'])
            if boleta:
                if boleta.quality_check_id:
                    if boleta.quality_check_id!=vals[id]:
                        raise UserError('La boleta ya tiene un control de calidad asociado')
                else:
                    boleta.write({'quality_check_id':vals[id]})
        return super(unispice_quality_check, self).write(vals)

    @api.depends('quality_ids','product_id','lot_id','boleta_id','muestra')
    def calcular_totales(self):
        for r in self:            
            total_producto=0
            if r.product_id:
                if 'Materia Prima' in r.product_id.categ_id.display_name:
                    if r.boleta_id:
                        lotes=self.env['stock.production.lot'].search([('boleta_id','=',r.boleta_id.id)])
                        for l in lotes:
                            total_producto=total_producto+l.product_qty
                else:
                    if r.lot_id:
                        total_producto=total_producto+r.lot_id.product_qty
            porcentaje=0.0
            total=0.0
            r.lote_total=total_producto
            for l in r.quality_ids:
                l.compute_percentaje()
            for l in r.quality_ids:
                total=total+l.proyectado
            r.total_afectado=total
            if total_producto>0:
                porcentaje=total/total_producto
            r.porcentaje=porcentaje
            
            




    @api.onchange('product_id','workcenter_id')
    def change_product(self):
        for r in self:
            r.quality_ids.unlink()
            if r.workorder_id:
                lst=self.env['unispice.quatily_item'].search([('proceso_id','=',r.workcenter_id.id),('tipo','=','Proceso')])
                for p in lst:
                    dic={}
                    dic['name']=p.name
                    dic['aprobado']=False
                    dic['check_id']=r.id
                    dic['item_id']=p.id
                    self.env['unispice.quatily_check_item'].create(dic)
            else:
                if r.product_id:
                    if 'Materia Prima' in r.product_id.categ_id.display_name:
                        if r.product_id.x_grupo_mp:
                            lst=self.env['unispice.quatily_item'].search([('x_grupo_mp','=',r.product_id.x_grupo_mp),('tipo','=','Materia Prima')])
                            for p in lst:
                                dic={}
                                dic['name']=p.name
                                dic['aprobado']=False
                                dic['check_id']=r.id
                                dic['item_id']=p.id
                                self.env['unispice.quatily_check_item'].create(dic)
                    else:
                        lst=self.env['unispice.quatily_item'].search([('categoria_id','=',r.product_id.categ_id.id),('tipo','=','Producto')])
                        for p in lst:
                            dic={}
                            dic['name']=p.name
                            dic['aprobado']=False
                            dic['check_id']=r.id
                            dic['item_id']=p.id
                            self.env['unispice.quatily_check_item'].create(dic)
