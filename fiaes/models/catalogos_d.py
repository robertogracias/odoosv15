from odoo import api, models, fields, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID

class cuenta(models.Model):
    _inherit = 'account.account'
    tipo_de_aplicacion=fields.Selection(selection=[('General','General'),('Detall','Detalle')])
    tipo_de_saldo=fields.Selection(selection=[('Deudor','Deudor'),('Acreedor','Acreedor')])

class proyecto(models.Model):
    _name = "fiaes.proyecto"
    _description='Proyecto Compensacion'
    name=fields.Char("Proyecto")
    fuentes_ids=fields.Many2many('fiaes.fuente','Fuentes')
    codigo=fields.Char("Codigo")
    departamento_id=fields.Many2one(comodel_name='fiaes.departamento', string='Departamento')
    municipio_id=fields.Many2one(comodel_name='fiaes.municipio', string='Municipio')
    coordenadas_latitud=fields.Float("Latitud",digits=(20,7))
    coordenadas_longitud=fields.Float("Longitud",digits=(20,7))
    afectacion=fields.Text("Tipo de afectacion")
    ejecutora=fields.Many2one(comodel_name='res.partner', string='Ejecutora')
    contrapartida=fields.Float("Contrapartida")
    aliados=fields.Many2many('res.partner','Aliados')
    estado=fields.Selection(selection=[('Estado1', 'Estado1')
                                        ,('Estado2', 'Estado2')]
                                        , string='Estado')



class costo(models.Model):
    _name = "fiaes.costo"
    _description='Centro de costo'
    name = fields.Char('Centro de costo')

class territorio(models.Model):
    _name = "fiaes.territorio"
    _description = "Territorios"
    name = fields.Char('Territorio')
    descripcion=fields.Text("Descripcion")
    coordenadas_latitud=fields.Float("Latitud",digits=(20,7))
    coordenadas_longitud=fields.Float("Longitud",digits=(20,7))
