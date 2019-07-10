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
    _inherit='project.project'
    fuentes_ids=fields.One2many('fiaes.fuente','proyecto_id','Fuentes')

class costo(models.Model):
    _name = "fiaes.costo"
    _description='Centro de costo'
    name = fields.Char('Centro de costo')

class territorio(models.Model):
    _name = "fiaes.territorio"
    _description = "Territorios"
    name = fields.Char('Territorio')
