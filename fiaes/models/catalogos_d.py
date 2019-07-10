from odoo import api, models, fields, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID

class cuenta(models.Model):
    _inherit = 'account.account'
    tipo_de_cuenta=fields.Selection(selection=[('Activo','Activo')
                                                ,('Pasivo','Pasivo')
                                                ,('Capital','Capital')
                                                ,('Resultado Deudor','Resultado Deudor')
                                                ,('Resultado Acreedor','Resultado Acreedor')
                                                ,('Cuenta Liquidadora','Cuenta Liquidadora')
                                                ,('Cuenta de Orden','Cuenta de Orden')],string='Tipo de cuenta')
    tipo_de_aplicacion=fields.Selection(selection=[('General','General'),('Detall','Detalle')])
    tipo_de_saldo=fields.Selection(selection=[('Deudor','Deudor'),('Acreedor','Acreedor')])
