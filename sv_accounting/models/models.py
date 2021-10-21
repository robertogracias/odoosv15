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


    
class odoofiscalsv_prodcut(models.Model):
    _inherit='product.template'
    fiscal_type=fields.Selection(selection=[('Servicio','Servicio'),('Tangible','Tangible')],string="Tipo Fiscal del producto")

class odoofiscalsv_taxgroup(models.Model):
    _inherit='account.tax.group'
    code=fields.Char("Codigo")
    company_id=fields.Many2one('res.company',string="Company")

class odoosv_user(models.Model):
    _inherit='res.company'
    
    #Cuentas
    account_iva_consumidor_id=fields.Many2one('account.account',string="Cuenta de IVA consumidor (Venta)")
    account_iva_contribuyente_id=fields.Many2one('account.account',string="Cuenta de IVA contribuyente (Venta)")
    account_iva_compras_id=fields.Many2one('account.account',string="Cuenta de IVA Compras (Compra)")
    account_retencion_id=fields.Many2one('account.account',string="Cuenta de Retencion (Venta)")
    account_perceccion_id=fields.Many2one('account.account',string="Cuenta de Perseccion (Compras)")
    account_isr_id=fields.Many2one('account.account',string="Cuenta de ISR (Compras)")

    #impuestos
    tax_iva_consumidor_id=fields.Many2one('account.tax',string="Impuesto de IVA consumidor (Venta)")
    tax_iva_contribuyente_id=fields.Many2one('account.tax',string="Impuesto de IVA contribuyente (Venta)")
    tax_iva_compras_id=fields.Many2one('account.tax',string="Impuesto de IVA Compras (Compra)")
    tax_retencion_id=fields.Many2one('account.tax',string="Impuesto de Retencion (Venta)")
    tax_perceccion_id=fields.Many2one('account.tax',string="Impuesto de Perseccion (Compras)")
    tax_isr_id=fields.Many2one('account.tax',string="Impuesto de ISR (Compras)")
    tax_exento_compra_id=fields.Many2one('account.tax',string="Impuesto de Exento (Compra)")
    tax_exento_venta_id=fields.Many2one('account.tax',string="Impuesto de Exento (Venta)")
    tax_nosujeto_compra_id=fields.Many2one('account.tax',string="Impuesto No Sujeto (Compras)")
    tax_nosujeto_venta_id=fields.Many2one('account.tax',string="Impuesto No Sujeto (Venta)")
    tax_base_tangible_compra=fields.Many2one('account.tax',string="Impuesto de base tangible (Compra)")
    tax_base_tangible_venta=fields.Many2one('account.tax',string="Impuesto de base tangible (Venta)")
    tax_base_servicio_compra=fields.Many2one('account.tax',string="Impuesto de base servicio (Compra)")
    tax_base_servicio_venta=fields.Many2one('account.tax',string="Impuesto de base servicio (Venta)")

    #grupos de impuestos
    tax_group_iva_id=fields.Many2one('account.tax.group',string=" Grupo de impuestos IVA")
    tax_group_retencion_id=fields.Many2one('account.tax.group',string=" Grupo de impuestos Retencion")
    tax_group_persecion_id=fields.Many2one('account.tax.group',string=" Grupo de impuestos Precepcion")
    tax_group_isr_id=fields.Many2one('account.tax.group',string=" Grupo de impuestos ISR")
    tax_group_exento_id=fields.Many2one('account.tax.group',string=" Grupo de impuestos Exento")
    tax_group_nosujeto_id=fields.Many2one('account.tax.group',string=" Grupo de impuestos No Sujeto")

    #posiciones fiscales
    fiscal_position_no_contribuyente_id=fields.Many2one('account.fiscal.position',string="Posicion fiscal no contribuyente")
    fiscal_position_pyme_natural_id=fields.Many2one('account.fiscal.position',string="Posicion fiscal pyme natural")
    fiscal_position_pyme_juridico_id=fields.Many2one('account.fiscal.position',string="Posicion fiscal pyme juridico")
    fiscal_position_grande_natural_id=fields.Many2one('account.fiscal.position',string="Posicion fiscal grande natural")
    fiscal_position_grande_juridico_id=fields.Many2one('account.fiscal.position',string="Posicion fiscal grande juridico")
    fiscal_position_exento_id=fields.Many2one('account.fiscal.position',string="Posicion fiscal exento")
    fiscal_position_extrangero_id=fields.Many2one('account.fiscal.position',string="Posicion fiscal extranjero")

    #formatos de reportes
    formato_ccf=fields.Char("formato de CCF")
    formato_factura=fields.Char("formato de Factura")
    formato_exportacion=fields.Char("formato de Exportacion")
    formato_notacredito=fields.Char("formato de Nota de Credito")


    def create_tax_groups(self):
        for r in self:
            if not r.tax_group_iva_id:
                g=self.env['account.tax.group'].create({'name':'IVA'+'-'+r.name,'code':'iva','company_id':r.id})
                r.tax_group_iva_id=g.id
            if not r.tax_group_retencion_id:
                g=self.env['account.tax.group'].create({'name':'Retencion'+'-'+r.name,'code':'retencion','company_id':r.id})
                r.tax_group_retencion_id=g.id
            if not r.tax_group_persecion_id:
                g=self.env['account.tax.group'].create({'name':'Percepcion'+'-'+r.name,'code':'Percepcion','company_id':r.id})
                r.tax_group_persecion_id=g.id
            if not r.tax_group_isr_id:
                g=self.env['account.tax.group'].create({'name':'ISR'+'-'+r.name,'code':'ISR','company_id':r.id})
                r.tax_group_isr_id=g.id
            if not r.tax_group_exento_id:
                g=self.env['account.tax.group'].create({'name':'Exento'+'-'+r.name,'code':'Exento','company_id':r.id})
                r.tax_group_exento_id=g.id
            if not r.tax_group_nosujeto_id:
                g=self.env['account.tax.group'].create({'name':'No Sujeto'+'-'+r.name,'code':'No Sujeto','company_id':r.id})
                r.tax_group_nosujeto_id=g.id

    def create_tax(self):
        for r in self:
            #Iva Consumidor            
            dic={}
            dic['name']='IVA Consumidor.'
            dic['amount_type']='percent'
            dic['type_tax_use']='sale'
            dic['amount']=13
            dic['description']='Iva'
            dic['tax_group_id']=r.tax_group_iva_id.id
            dic['company_id']=r.id
            tax=r.tax_iva_consumidor_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_iva_consumidor_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_iva_consumidor_id.id,'invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_iva_consumidor_id.id,'refund_tax_id':tax.id})

            #Iva contribuyente            
            dic={}
            dic['name']='IVA Contribuyente.'
            dic['amount_type']='percent'
            dic['type_tax_use']='sale'
            dic['amount']=13
            dic['description']='Iva'
            dic['tax_group_id']=r.tax_group_iva_id.id
            dic['company_id']=r.id
            tax=r.tax_iva_contribuyente_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_iva_contribuyente_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_iva_contribuyente_id.id,'invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_iva_contribuyente_id.id,'refund_tax_id':tax.id})


            #Iva Compras            
            dic={}
            dic['name']='IVA Compras.'
            dic['amount_type']='percent'
            dic['type_tax_use']='purchase'
            dic['amount']=13
            dic['description']='Iva'
            dic['tax_group_id']=r.tax_group_iva_id.id
            dic['company_id']=r.id
            tax=r.tax_iva_compras_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_iva_compras_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_iva_compras_id.id,'invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_iva_compras_id.id,'refund_tax_id':tax.id})


            #Iva retencion            
            dic={}
            dic['name']='Retencion 1%'
            dic['amount_type']='percent'
            dic['type_tax_use']='sale'
            dic['amount']=1
            dic['description']='Retencion'
            dic['tax_group_id']=r.tax_group_retencion_id.id
            dic['company_id']=r.id
            tax=r.tax_retencion_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_retencion_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_retencion_id.id,'invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_retencion_id.id,'refund_tax_id':tax.id})

            #IVA percepcion            
            dic={}
            dic['name']='Percepcion 1%'
            dic['amount_type']='percent'
            dic['type_tax_use']='purchase'
            dic['amount']=1
            dic['description']='Percepcion'
            dic['tax_group_id']=r.tax_group_persecion_id.id
            dic['company_id']=r.id
            tax=r.tax_perceccion_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_perceccion_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_perceccion_id.id,'invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_perceccion_id.id,'refund_tax_id':tax.id})

            #ISR            
            dic={}
            dic['name']='ISR 10%'
            dic['amount_type']='percent'
            dic['type_tax_use']='purchase'
            dic['amount']=-10
            dic['description']='ISR'
            dic['tax_group_id']=r.tax_group_isr_id.id
            dic['company_id']=r.id
            tax=r.tax_isr_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_isr_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_isr_id.id,'invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'tax','account_id':r.account_isr_id.id,'refund_tax_id':tax.id})

            #exento compra           
            dic={}
            dic['name']='Exento compra'
            dic['amount_type']='percent'
            dic['type_tax_use']='purchase'
            dic['amount']=0
            dic['description']='Exento'
            dic['tax_group_id']=r.tax_group_exento_id.id
            dic['company_id']=r.id
            tax=r.tax_exento_compra_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_exento_compra_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','refund_tax_id':tax.id})

            #exento venta           
            dic={}
            dic['name']='Exento venta'
            dic['amount_type']='percent'
            dic['type_tax_use']='sale'
            dic['amount']=0
            dic['description']='Exento'
            dic['tax_group_id']=r.tax_group_exento_id.id
            dic['company_id']=r.id
            tax=r.tax_exento_venta_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_exento_venta_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','refund_tax_id':tax.id})


            #no sujeto compra           
            dic={}
            dic['name']='No Sujeto Compra'
            dic['amount_type']='percent'
            dic['type_tax_use']='purchase'
            dic['amount']=0
            dic['description']='No Sujeto'
            dic['tax_group_id']=r.tax_group_nosujeto_id.id
            dic['company_id']=r.id
            tax=r.tax_nosujeto_compra_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_nosujeto_compra_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','refund_tax_id':tax.id})

            #no sujeto venta           
            dic={}
            dic['name']='No Sujeto Venta'
            dic['amount_type']='percent'
            dic['type_tax_use']='sale'
            dic['amount']=0
            dic['description']='No Sujeto'
            dic['tax_group_id']=r.tax_group_nosujeto_id.id
            dic['company_id']=r.id
            tax=r.tax_nosujeto_venta_id
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_nosujeto_venta_id':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','refund_tax_id':tax.id})

            #base tangible compra           
            dic={}
            dic['name']='Base Tangible Compra'
            dic['amount_type']='percent'
            dic['type_tax_use']='purchase'
            dic['amount']=0
            dic['description']='Base T'
            dic['tax_group_id']=r.tax_group_nosujeto_id.id
            dic['company_id']=r.id
            tax=r.tax_base_tangible_compra
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_base_tangible_compra':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','refund_tax_id':tax.id})

            #base Tangible venta           
            dic={}
            dic['name']='Base Tangible Venta'
            dic['amount_type']='percent'
            dic['type_tax_use']='sale'
            dic['amount']=0
            dic['description']='Base T'
            dic['tax_group_id']=r.tax_group_nosujeto_id.id
            dic['company_id']=r.id
            tax=r.tax_base_tangible_venta
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_base_tangible_venta':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','refund_tax_id':tax.id})


            #base servicio compra           
            dic={}
            dic['name']='Base Servicio Compra'
            dic['amount_type']='percent'
            dic['type_tax_use']='purchase'
            dic['amount']=0
            dic['description']='Base T'
            dic['tax_group_id']=r.tax_group_nosujeto_id.id
            dic['company_id']=r.id
            tax=r.tax_base_servicio_compra
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_base_servicio_compra':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','refund_tax_id':tax.id})

            #base Servicio venta           
            dic={}
            dic['name']='Base Servicio Venta'
            dic['amount_type']='percent'
            dic['type_tax_use']='sale'
            dic['amount']=0
            dic['description']='Base T'
            dic['tax_group_id']=r.tax_group_nosujeto_id.id
            dic['company_id']=r.id
            tax=r.tax_base_servicio_venta
            if tax:
                tax.write(dic)
            else:
                tax=self.env['account.tax'].create(dic)
                r.write({'tax_base_servicio_venta':tax.id})
            tax.invoice_repartition_line_ids.unlink()
            tax.refund_repartition_line_ids.unlink()
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','invoice_tax_id':tax.id})
            self.env['account.tax.repartition.line'].create({'factor_percent':100,'repartition_type':'base','refund_tax_id':tax.id})


    def create_fiscal_position(self):
        for r in self:
            #no contribuyente:
            dic={}
            dic['name']='No Contribuyente'
            dic['company_id']=r.id
            fp=r.fiscal_position_no_contribuyente_id
            if fp:
                fp.write(dic)
            else:
                fp=self.env['account.fiscal.position'].create(dic)
                r.write({'fiscal_position_no_contribuyente_id':fp.id})
            fp.tax_ids.unlink()
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_nosujeto_compra_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_iva_consumidor_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_isr_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_iva_consumidor_id.id})
            
            #Pyme Natura:
            dic={}
            dic['name']='Pyme Natural'
            dic['company_id']=r.id
            fp=r.fiscal_position_pyme_natural_id
            if fp:
                fp.write(dic)
            else:
                fp=self.env['account.fiscal.position'].create(dic)
                r.write({'fiscal_position_pyme_natural_id':fp.id})
            fp.tax_ids.unlink()
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_iva_contribuyente_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_isr_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_iva_contribuyente_id.id})
            
            #Pyme Juridico:
            dic={}
            dic['name']='Pyme Juridico'
            dic['company_id']=r.id
            fp=r.fiscal_position_pyme_juridico_id
            if fp:
                fp.write(dic)
            else:
                fp=self.env['account.fiscal.position'].create(dic)
                r.write({'fiscal_position_pyme_juridico_id':fp.id})
            fp.tax_ids.unlink()
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_iva_contribuyente_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_iva_contribuyente_id.id})
            
            #Grande Natural:
            dic={}
            dic['name']='Grande Natural'
            dic['company_id']=r.id
            fp=r.fiscal_position_grande_natural_id
            if fp:
                fp.write(dic)
            else:
                fp=self.env['account.fiscal.position'].create(dic)
                r.write({'fiscal_position_grande_natural_id':fp.id})
            fp.tax_ids.unlink()
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_perceccion_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_iva_contribuyente_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_retencion_id.id})
            
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_retencion_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_isr_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_iva_contribuyente_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_perceccion_id.id})
            



            #Grande Juridico:
            dic={}
            dic['name']='Grande Juridico'
            dic['company_id']=r.id
            fp=r.fiscal_position_grande_juridico_id
            if fp:
                fp.write(dic)
            else:
                fp=self.env['account.fiscal.position'].create(dic)
                r.write({'fiscal_position_grande_juridico_id':fp.id})
            fp.tax_ids.unlink()
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_perceccion_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_iva_contribuyente_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_retencion_id.id})
            
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_retencion_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_iva_contribuyente_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_perceccion_id.id})
            


            #Exento:
            dic={}
            dic['name']='Exento'
            dic['company_id']=r.id
            fp=r.fiscal_position_exento_id
            if fp:
                fp.write(dic)
            else:
                fp=self.env['account.fiscal.position'].create(dic)
                r.write({'fiscal_position_exento_id':fp.id})
            fp.tax_ids.unlink()
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_exento_venta_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_iva_compras_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_exento_venta_id.id})
            

            #Exento:
            dic={}
            dic['name']='Extrangero'
            dic['company_id']=r.id
            fp=r.fiscal_position_extrangero_id
            if fp:
                fp.write(dic)
            else:
                fp=self.env['account.fiscal.position'].create(dic)
                r.write({'fiscal_position_extrangero_id':fp.id})
            fp.tax_ids.unlink()
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_compra.id,'tax_dest_id':r.tax_exento_compra_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_tangible_venta.id,'tax_dest_id':r.tax_exento_venta_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_compra.id,'tax_dest_id':r.tax_exento_compra_id.id})
            self.env['account.fiscal.position.tax'].create({'position_id':fp.id,'company_id':r.id,'tax_src_id':r.tax_base_servicio_venta.id,'tax_dest_id':r.tax_exento_venta_id.id})
            
    def configure_settings(self):
        for r in self:
            settings=self.env['res.config.settings'].search([('company_id','=',r.id)],limit=1)
            if settings:
                dic={}
                dic['sale_tax_id']=r.tax_base_tangible_venta.id
                dic['purchase_tax_id']=r.tax_base_tangible_compra.id
                settings.write(dic)

    def create_docs(self):
        for r in self:
            #factura
            dic={}
            factura=self.env['odoosv.fiscal.document'].search([('company_id','=',r.id),('name','=','Factura')],limit=1)
            if not factura:
                dic['name']='Factura'
                dic['company_id']=r.id
                dic['tipo_movimiento']='out_invoice'
                dic['formato']='Factura'
                self.env['odoosv.fiscal.document'].create(dic)
            #ccf
            dic={}
            ccf=self.env['odoosv.fiscal.document'].search([('company_id','=',r.id),('name','=','CCF')],limit=1)
            if not factura:
                dic['name']='CCF'
                dic['company_id']=r.id
                dic['tipo_movimiento']='out_invoice'
                dic['formato']='CCF'
                dic['validacion']="""
if not partner.nrc:
    raise ValidationError('El cliente debe tener NRC')
                """
                self.env['odoosv.fiscal.document'].create(dic)
            dic={}
            exportacion=self.env['odoosv.fiscal.document'].search([('company_id','=',r.id),('name','=','Exportacion')],limit=1)
            if not factura:
                dic['name']='Exportacion'
                dic['company_id']=r.id
                dic['tipo_movimiento']='out_invoice'
                dic['formato']='Exportacion'
                dic['validacion']="""
if not partner.tipo_localidad=='NoDomiciliado':
    raise ValidationError('El cliente no debe ser local')
                """
                self.env['odoosv.fiscal.document'].create(dic)
            dic={}
            notacredito=self.env['odoosv.fiscal.document'].search([('company_id','=',r.id),('name','=','Nota de Credito')],limit=1)
            if not factura:
                dic['name']='Nota de Credito'
                dic['company_id']=r.id
                dic['tipo_movimiento']='out_refund'
                dic['formato']='NotaCredito'
                dic['validacion']="""
if not partner.nrc:
    raise ValidationError('El cliente debe tener NRC')
                """
                self.env['odoosv.fiscal.document'].create(dic)
            dic={}
            devolucion=self.env['odoosv.fiscal.document'].search([('company_id','=',r.id),('name','=','Devolucion')],limit=1)
            if not factura:
                dic['name']='Devolucion'
                dic['company_id']=r.id
                dic['tipo_movimiento']='out_refund'
                dic['formato']='Devolucion'
                self.env['odoosv.fiscal.document'].create(dic)
    #Aplicar todas las configuraciones
    def configurar(self):
        for r in self:
            r.create_tax_groups()
            r.create_tax()
            r.create_fiscal_position()
            r.configure_settings()
            r.create_docs()


class odoosv_partner(models.Model):
    _inherit='res.partner'
    contribuyente=fields.Boolean("Contribuyente")
    tipo_persona=fields.Selection(selection=[('Natural','Natural'),('Juridico','Juridico')],string="Tipo de persona")
    tamanio_empresa=fields.Selection(selection=[('PYME','PYME'),('Grande','Grande')],string="Tamaño de la empresa")
    tipo_fiscal=fields.Selection(selection=[('Gravado','Gravado'),('Exento','Exento')],string="Tipo fiscal")
    tipo_localidad=fields.Selection(selection=[('Local','Local'),('NoDomiciliado','NoDomiciliado')],string="Localidad")

class odoosv_move(models.Model):
    _inherit='account.move'
    tipo_documento_id=fields.Many2one('odoosv.fiscal.document',string="Tipo de Documento")

    @api.constrains('tipo_documento_id','partner_id','amount_total')
    def _check_restriciones(self):
        for r in self:
            if r.move_type in ('in_invoice','in_refund','out_invoice','out_refund'):
                if not r.tipo_documento_id:
                    raise ValidationError('Debe especificare un tipo de documento')
                else:
                    dic={}
                    dic['move']=r
                    dic['partner']=r.partner_id
                    dic['ValidationError']=ValidationError
                    if r.tipo_documento_id.validacion:
                        safe_eval(r.tipo_documento_id.validacion,dic, mode='exec')
    
class odoosv_documento(models.Model):
    _name='odoosv.fiscal.document'
    _description='Tipos de documentos de la localizacion'
    name=fields.Char('Nombre del documento')
    formato=fields.Char('Formato del documento')
    tipo_movimiento=fields.Selection(selection=[('in_invoice','Factura Proveedor'),('out_invoice','Factura Cliente'),('in_fefund','Nota Credito Proveedor'),('out_fefund','Nota Credito Cliente'),('entry','Entry')],string="Tipo Documento")
    validacion=fields.Text("Codigo de Validacion")
    company_id=fields.Many2one('res.company',string="Company")

    
            


