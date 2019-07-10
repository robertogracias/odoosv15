# -*- coding: utf-8 -*-
##############################################################################


from odoo import api, models, fields, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


class contacto(models.Model):
    _inherit = 'res.partner'

class profesion(models.Model):
    _name='fiaes.profesion'
    _description='Profesion asociada al empleado'
    name=fields.Char("Profesion")

class beneficiario(models.Model):
    _name='fiaes.beneficiario'
    _description='Benefiario'
    name=fields.Char("Nombre")
    empleado_id=fields.Many2one(comodel_name='hr.employee', string='Empleado')
    parentesco=fields.Selection(selection=[('Hijo/a', 'Hijo/a')
                                        ,('Padre/Madre', 'Padre/Madre')
                                        ,('Esposo/a', 'Esposo/a')
                                        ,('Otro', 'Otro')]
                                        , string='Parentesco')

class departamento(models.Model):
    _name='fiaes.departamento'
    _description='Departamento'
    name=fields.Char("Departamento")

class municipio(models.Model):
    _name='fiaes.municipio'
    _description='Municipio'
    name=fields.Char("Municipio")
    departamento=fields.Many2one(comodel_name='fiaes.departamento', string='Departamento')


class empleado(models.Model):
    _inherit = 'hr.employee'
    codigo=fields.Integer("Codigo empleado")
    nombres=fields.Char("Nombres")
    apellidos=fields.Char("Apellidos")
    name=fields.Char("Nombre",compute='compute_name')
    dui=fields.Char("DUI")
    nit=fields.Char("NIT")
    licencia=fields.Char("Licencia")
    fecha_licencia=fields.Date("Fecha vencimiento licencia")
    tipo_sangre=fields.Char("Tipo de sangre")
    profesion_id=fields.Many2one(comodel_name='fiaes.profesion', string='Profesion')
    departamento_id=fields.Many2one(comodel_name='fiaes.departamento', string='Departamento')
    municipio_id=fields.Many2one(comodel_name='fiaes.municipio', string='Municipio')
    direccion=fields.Char("Direccion")
    beneficiarios_ids=fields.One2many('fiaes.beneficiario','empleado_id', 'Beneficiarios')
    fecha_ingreso=fields.Date("Fecha de Ingreso")
    fecha_retiro=fields.Date("Fecha de Retiro")
    causas_despido=fields.Text("Causas de despido")
    cuenta_bancaria=fields.Char("Cuenta Bancaria")
    cuenta_tipo=fields.Selection(selection=[('Ahorro', 'Ahorro')
                                        ,('Corriente', 'Corriente')]
                                        , string='Parentesco')
    cuenta_banco_id=fields.Many2one(comodel_name='res.partner.bank', string='Banco')


    def compute_name(self):
        self.name = self.nombre+' '+self.apellidos


class fuente(models.Model):
    _name='fiaes.fuente'
    _description='Fuente de financiamiento'
    name= fields.Float("Fuente")


class contrato(models.Model):
    _inherit = 'hr.contract'
    sueldo_dia= fields.Float("Sueldo por dia")
    sueldo_hora=fields.Float("Sueldo por hora")
    fuente_id=fields.Many2one(comodel_name='fiaes.fuente', string='Fuente')




class contacto(models.Model):
    _inherit = 'res.partner'
    nombres=fields.Char("Nombres")
    apellidos=fields.Char("Apellidos")
    nombre_comercial=fields.Char("Nombre comercial")
    nit=fields.Char("NIT")
    nrc=fields.Char("NRC")
    representante_nombre=fields.Char("Representante legal")
    representante_nit=fields.Char("NIT del representante")
    representante_dui=fields.Char("NRC del representante")
    giro=fields.Char("Giro")


class usovehiculo(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    solicitante_id=fields.Many2one(comodel_name='hr.employee', string='Solicitante')
    fecha_solicitud=fields.Date("Fecha Solicitud")
    destino=fields.Char("Destino")
    mision_oficial=fields.Char("Mision Oficial")
    fecha_salida=fields.Date("Fecha Salida")
    fecha_regreso=fields.Date("Fecha Regreso")
    odometro_regreso=fields.Integer("Kilometraje de regreso")
    asistieron_ids=fields.Many2many(comodel_name='hr.employee', string='Asistieron')
    encargado_revision_id=fields.Many2one(comodel_name='hr.employee', string='Encargado de revision')
    encargado_autorizacion_id=fields.Many2one(comodel_name='hr.employee', string='Encargado de autorizacion')
