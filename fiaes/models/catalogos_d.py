from odoo import api, models, fields, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


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





class territorio_cordenadas(models.Model):
    _name = "fiaes.territorio_cordenadas"
    _description = "Cordenadas del poligo que define a cada rerritorio"
    name = fields.Char('Descripcion')
    coordenadas_latitud=fields.Float("Latitud",digits=(20,7))
    coordenadas_longitud=fields.Float("Longitud",digits=(20,7))
    territorio_id=fields.Many2one(comodel_name='fiaes.territorio', string='Territorio')


class territorio(models.Model):
    _name = "fiaes.territorio"
    _description = "Territorios"
    codigo = fields.Char('Codigo')
    name = fields.Char('Territorio')
    codigo = fields.Char('Codigo')
    descripcion=fields.Text("Descripcion")
    cordenada_ids=fields.One2many('fiaes.territorio_cordenadas','territorio_id', 'Cordenadas')
    contacto_ids=fields.Many2many(comodel_name='res.partner', relation='territorio_contacto_rel', string='Contactos')
    responsable_ids=fields.Many2many(comodel_name='hr.employee', relation='territorio_responsable_rel', string='Responsable')
    unidades_ids=fields.Many2many(comodel_name='hr.department', relation='territorio_deparment_rel', string='Unidades')
