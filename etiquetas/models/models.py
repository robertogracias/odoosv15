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


class etiqueta(models.Model):
    _name='etiquetas.label'
    _inherit='mail.thread'
    _description='Disenio de la etiequeta'
    name=fields.Char("Disenio",tracking=True)
    tipo=fields.Selection(selection=[('zpl','zpl'),('dml','dml'),('html','html'),('otro','otro')],defautl='zpl')
    contenido=fields.Text("Contenido")
    contenido_html=fields.Text("Contenido HTML")
    comment=fields.Text("Descripcion")

    def evaluate(self,product=False,lot=False,company=False):
        texto=''
        
        for r in self:
            if not r.contenido:
                continue
            textos=r.contenido.split(' ')
            if r.tipo=='html':
                textos=r.contenido_html.split(' ')
            textos_finales=[]
            dic={}
            dic['product']=product
            dic['lot']=lot
            dic['company']=company
            for t in textos:
                if len(t)==0:
                    continue
                if t[0]=='$':
                    variable=t[1:]
                    valor=str(safe_eval(variable, dic))
                    textos_finales.append(' '+valor)
                else:
                    textos_finales.append(' '+t)
            for t in textos_finales:
                texto=texto+t
        return texto

    
class etiqueta_grupo(models.Model):
    _name='etiquetas.group'
    _inherit='mail.thread'
    _description='Grupos de etiquetas'
    name=fields.Char("Grupo de etiqueta",tracking=True)
    product_tmpl_id=fields.Many2one(comodel_name='product.template', string="Producto")
    items_id=fields.One2many(comodel_name='etiquetas.group.item',inverse_name='group_id',string='Items')
    comment=fields.Text("Descripcion")

class etiqueta_grupo_item(models.Model):
    _name='etiquetas.group.item'
    _description='Grupos de etiquetas'
    name=fields.Char("Grupo de etiqueta")
    label_id=fields.Many2one(comodel_name='etiquetas.label', string="Etiqueta")
    quantity=fields.Integer("Productos por etiqueta",default=1)
    group_id=fields.Many2one(comodel_name='etiquetas.group', string="Grupo")
    sequence=fields.Integer("Orden")


class etiqueta_corrida(models.Model):
    _name='etiquetas.run'
    _inherit='mail.thread'
    _description='Ejecucion de editquetas'
    name=fields.Char("Ejecucion",copy=False)
    product_id=fields.Many2one(comodel_name='product.product', string="Producto")
    product_tmpl_id=fields.Many2one(comodel_name='product.template', related='product_id.product_tmpl_id', string="Producto")
    group_id=fields.Many2one(comodel_name='etiquetas.group', string="Grupo")
    items_id=fields.One2many(comodel_name='etiquetas.run.item',inverse_name='run_id',string='Items')
    lot_id=fields.Many2one(comodel_name='stock.production.lot', string="Lote")
    state=fields.Selection(selection=[('nuevo','nuevo'),('ejecutado','ejecutado'),('otro','otro')],default='nuevo')
    quantity=fields.Integer("Cantidad de productos",default=1)
    

    def run(self):
        self.ensure_one()
        if not self.lot_id :
            raise ValidationError('Debe tenerse seleccionado un lote')
        if self.state!='nuevo':
            raise ValidationError('La ejecucion ya fue ejecutada')
        for l in self.group_id.items_id:
            x=1
            y=l.quantity
            i=0
            texto=''
            while x<=self.quantity:
                x=x+y
                i=i+1
                texto=texto+l.label_id.evaluate(product=self.product_id,lot=self.lot_id,company=self.lot_id.company_id)
            dic={}
            dic['name']=l.name
            dic['quantity']=i
            dic['content']=texto
            dic['counter']=0
            dic['run_id']=self.id
            dic['tipo']=l.label_id.tipo
            self.env['etiquetas.run.item'].create(dic)
        self.write({'name':self.env['ir.sequence'].next_by_code('etiquetas.run'),'state':'ejecutado'})




class etiqueta_corrida_item(models.Model):
    _name='etiquetas.run.item'
    _description='Ejecucion de etiquetas'
    name=fields.Char("Etiqueta")
    quantity=fields.Integer("Cantidad de etiqueta")
    content=fields.Text("Contenido")
    counter=fields.Integer("Cantidad de impresiones")
    run_id=fields.Many2one(comodel_name='etiquetas.run', string="Ejecucion")
    tipo=fields.Selection(selection=[('zpl','zpl'),('dml','dml'),('html','html'),('otro','otro')],defautl='zpl')
    label_id=fields.Many2one(comodel_name='etiquetas.label', string="Etiqueta")
    
    
    def imprimir(self):
        self.ensure_one()
        self.write({'counter':self.counter+1})
        if self.tipo=='html':
            return {
                'type': 'ir.actions.report',
                'report_name':'etiquetas.action_etiqueta_pdf',
                'model':'etiquetas.run.item',
                'report_type':"qweb-pdf",
                } 

    def imprimirzpl(self):
        self.ensure_one()
        self.write({'counter':self.counter+1})
    

