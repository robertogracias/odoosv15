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
    name= fields.Char("Fuente")
    account_id=fields.Many2one(comodel_name='account.account', string='Cuenta asociada')


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
    departamento_id=fields.Many2one(comodel_name='fiaes.departamento', string='Departamento')
    municipio_id=fields.Many2one(comodel_name='fiaes.municipio', string='Municipio')
    representante_nombre=fields.Char("Representante legal")
    representante_nit=fields.Char("NIT del representante")
    representante_dui=fields.Char("NRC del representante")
    representante_nacionalidad=fields.Many2one(comodel_name='res.country', string='Nacionalidad del representante')
    representante_nacimiento=fields.Date("Fecha de nacimiento del representante legal")
    representante_profesion=fields.Char("Profesion del representante legal")
    contacto=fields.Char("Contacto")
    giro=fields.Char("Giro")

class vehiculo(models.Model):
    _inherit='fleet.vehicle'
    marca_id=fields.Many2one(comodel_name='fleet.vehicle.model.brand', related='model_id.brand_id',string='Marca',store='false')



class usovehiculo(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    solicitante_id=fields.Many2one(comodel_name='hr.employee', string='Solicitante')
    conductor_id=fields.Many2one(comodel_name='hr.employee', string='Conductor')
    fecha_solicitud=fields.Date("Fecha Solicitud")
    destino=fields.Char("Destino")
    mision_oficial=fields.Char("Mision Oficial")
    fecha_salida=fields.Date("Fecha Salida")
    fecha_regreso=fields.Date("Fecha Regreso")
    odometro_regreso=fields.Integer("Kilometraje de regreso")
    asistieron_ids=fields.Many2many(comodel_name='hr.employee', string='Asistieron')
    encargado_revision_id=fields.Many2one(comodel_name='hr.employee', string='Encargado de revision')
    encargado_autorizacion_id=fields.Many2one(comodel_name='hr.employee', string='Encargado de autorizacion')

class aspectorevisar(models.Model):
    _name='fiaes.vehiculo_aspecto'
    _description='Aspecto a Revisar'
    name=fields.Char("Aspecto a revisar")

class mantenimiento(models.Model):
    _inherit='fleet.vehicle.log.services'
    solicitante_id=fields.Many2one(comodel_name='hr.employee', string='Solicitante')
    descripcion=fields.Text('Descripcion')
    marca=fields.Many2one(comodel_name='fleet.vehicle.model.brand', related='vehicle_id.marca_id',string='Marca',store='false')
    modelo=fields.Many2one(comodel_name='fleet.vehicle.model', related='vehicle_id.model_id',string='Model',store='false')
    placa=fields.Char(related='vehicle_id.license_plate',string='Placa',store='false')
    taller_id=fields.Many2one(comodel_name='res.partner', string='Taller')
    taller_contacto=fields.Char(related='taller_id.contacto',string='Contacto del taller',store='false')
    taller_direccion=fields.Char(related='taller_id.street',string='Contacto del taller',store='false')
    taller_telefono=fields.Char(related='taller_id.phone',string='Contacto del taller',store='false')
    salida_fecha=fields.Date("Fecha salida")
    salida_km=fields.Integer("Kilometraje de salida")
    salida_gas=fields.Float("Combustible de salida")
    retorno_fecha=fields.Date("Fecha retorno")
    retorno_km=fields.Integer("Kilometraje de retorno")
    retorno_gas=fields.Float("Combustible de retorno")
    diagnostico=fields.Text("Diagnostico")
    apecto_ids=fields.Many2many(comodel_name='fiaes.vehiculo_aspecto', string='Aspectos a revisar')
    salida_encargado_id=fields.Many2one(comodel_name='hr.employee', string='Encargado de salida')
    retorno_encargado_id=fields.Many2one(comodel_name='hr.employee', string='Encargado de recepcion')


class activofijo(models.Model):
    _inherit='account.asset.asset'
    responsable_id=fields.Many2one(comodel_name='hr.employee', string='Responsable')
    ubicacion_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion')

class documento(models.Model):
    _inherit='ir.attachment'
    version=fields.Integer("Version")

class compensacion(models.Model):
    _inherit='sale.order'
    nombre_comercial=fields.Char("Nombre comercial",related='partner_id.nombre_comercial',store='fase')
    nit=fields.Char("NIT",related='partner_id.nit',store='fase')
    representante_nombre=fields.Char("Representante legal",related='partner_id.representante_nombre',store='fase')
    representante_nit=fields.Char("NIT del representante",related='partner_id.representante_nit',store='fase')
    representante_dui=fields.Char("NRC del representante",related='partner_id.representante_dui',store='fase')
    representante_nacionalidad=fields.Many2one(comodel_name='res.country', string='Nacionalidad del representante',related='partner_id.representante_nacionalidad',store='fase')
    representante_nacimiento=fields.Date("Fecha de nacimiento del representante legal",related='partner_id.representante_nacimiento',store='fase')
    representante_profesion=fields.Char("Profesion del representante legal",related='partner_id.representante_profesion',store='fase')
    departamento_id=fields.Many2one(comodel_name='fiaes.departamento', string='Departamento',related='partner_id.departamento_id',store='fase')
    municipio_id=fields.Many2one(comodel_name='fiaes.municipio', string='Municipio',related='partner_id.municipio_id',store='fase')
    poryecto_ambiental=fields.Char("Nombre del proyecto de compensacion ambiental")
    resolucion_marn=fields.Char("Numero de resolucion del MARN")
    resolucion_fecha=fields.Date("Fecha de resolucion del MARN")
    proyecto_direcion=fields.Char("Direccion del proyecto de compensacion ambiental")
    proyecto_departamento_id=fields.Many2one(comodel_name='fiaes.departamento', string='Departamento del proyecto de compensacion ambiental')
    proyecto_municipio_id=fields.Many2one(comodel_name='fiaes.municipio', string='Municipio del proyecto de compensacion ambiental')
    descripcion=fields.Text("Descripcion de la afectacion de la compensacion ambiental")
    rubro=fields.Char("Rubro de afectacion de la compensacion ambiental")
    area=fields.Char("Area strategica del FIAES a trabajar")
    valor=fields.Float("Valor del convenio")
    desembolsos=fields.Float("Numero de desembolsos")
    fianza=fields.Float("Monto de fianza de fiel cumplimento")
