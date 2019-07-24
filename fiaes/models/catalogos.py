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

class afp(models.Model):
    _name='fiaes.afp'
    _description='AFP'
    name=fields.Char("AFP")



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
    afp_id=fields.Many2one(comodel_name='fiaes.afp', string='AFP')
    direccion=fields.Char("Direccion")
    beneficiarios_ids=fields.One2many('fiaes.beneficiario','empleado_id', 'Beneficiarios')
    fecha_ingreso=fields.Date("Fecha de Ingreso")
    fecha_retiro=fields.Date("Fecha de Retiro")
    causas_despido=fields.Text("Causas de retiro")
    cuenta_bancaria=fields.Char("Cuenta Bancaria")
    cuenta_tipo=fields.Selection(selection=[('Ahorro', 'Ahorro')
                                        ,('Corriente', 'Corriente')]
                                        , string='Tipo de cuenta')
    cuenta_banco_id=fields.Many2one(comodel_name='res.partner.bank', string='Banco')
    dui_image=fields.Binary("Imagen del DUI")
    nit_image=fields.Binary("Imagen del NIT")


    def compute_name(self):
        self.name = self.nombre+' '+self.apellidos


class fuente(models.Model):
    _name='fiaes.fuente'
    _description='Fuente de financiamiento'
    name= fields.Char("Fuente")
    codigo= fields.Char("Codigo")
    account_id=fields.Many2one(comodel_name='account.account', string='Cuenta asociada')
    cuentabancaria_id=fields.Many2one(comodel_name='res.partner.bank', string='Cuenta bancaria asociada asociada')



class fuente_empleado(models.Model):
    _name='fiaes.fuente_empleado'
    _description='Fuente de financiamiento por empleado'
    name= fields.Char("Fuente")
    fuente_id=fields.Many2one(comodel_name='fiaes.fuente', string='Fuente')
    contrato_id=fields.Many2one(comodel_name='hr.contract', string='Contrato')
    porcentaje=fields.Float("Combustible de salida",digits=(20,10))


class contrato(models.Model):
    _inherit = 'hr.contract'
    sueldo_dia= fields.Float("Sueldo por dia")
    sueldo_hora=fields.Float("Sueldo por hora")
    sueldo_minuto=fields.Float("Sueldo por minuto")
    fuente_ids=fields.One2many('fiaes.fuente_empleado','contrato_id', 'Fuentes')


class telefono(models.Model):
    _name = 'fiaes.telefono'
    _description= 'Solicitud de vehiculo'
    name=fields.Char("Tipo de telefono")
    telefono=fields.Char("Phone")
    contacto_id=fields.Many2one(comodel_name='res.partner', string='Contacto')

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
    telefono_ids=fields.One2many('fiaes.telefono','contacto_id', 'Telefono')
    nit_image=fields.Binary("Imagen del NIT Sociedad")
    dui_rep_image=fields.Binary("Imagen del DUI del representante legal")
    nit_rep_image=fields.Binary("Imagen del NIT del representante legal")
    tipo=fields.Selection(selection=[('Aliado', 'Aliado')
                                        ,('Donante', 'Donante')
                                        ,('Titular', 'Titular')
                                        ,('Proveedor', 'Proveedor')]
                                        , string='Tipo de solicitante')

class vehiculo(models.Model):
    _inherit='fleet.vehicle'
    marca_id=fields.Many2one(comodel_name='fleet.vehicle.model.brand', related='model_id.brand_id',string='Marca',store='false')
    clase_id=fields.Many2one(comodel_name='fiaes.vehiculo_clase', string='Clase')
    tipo_id=fields.Many2one(comodel_name='fiaes.vehiculo_tipo', string='Tipo')
    motor=fields.Char("Motor #")
    chasis=fields.Char("Chasis #")
    activo_id=fields.Many2one(comodel_name='account.asset.asset', string='Activo')
    tarjeta=fields.Binary("Tarjeta de circulacion")
    servicios_km_ids=fields.One2many('fiaes.vehiculo_servicio','vehicle_id', 'Kilometrajes por servicio')

class servicio_kilometraje(models.Model):
    _name = 'fiaes.vehiculo_servicio'
    _description= 'Kilometrajes por servicio'
    name=fields.Char("Comentario")
    servicio=fields.Many2one(comodel_name='fleet.service.type', string='Servicio')
    kilometraje=fields.Integer("Kilometraje entre servicios")
    vehicle_id=fields.Many2one(comodel_name='fleet.vehicle', string='Vehiculo')



class vehiculo(models.Model):
    _inherit='fleet.vehicle'
    marca_id=fields.Many2one(comodel_name='fleet.vehicle.model.brand', related='model_id.brand_id',string='Marca',store='false')



class usovehiculo(models.Model):
    _name = 'fiaes.solicitud_vehiculo'
    _inherit= ['mail.thread']
    _description= 'Solicitud de vehiculo'
    name=fields.Char("Referencia")
    solicitante_tipo=fields.Selection(selection=[('Empleado', 'Empleado')
                                        ,('Contacto', 'Contacto')]
                                        , string='Tipo de solicitante')
    solicitante_employee_id=fields.Many2one(comodel_name='hr.employee', string='Solicitante')
    solicitante_partner_id=fields.Many2one(comodel_name='res.partner', string='Solicitante')
    vehicle_id=fields.Many2one(comodel_name='fleet.vehicle', string='Vehiculo')
    vehicle_name=fields.Char("Vehiculo",compute='get_vehicle')
    solicitante=fields.Char(string='Solicitante',compute='get_solicitante')
    source_email=fields.Char(string='Email',compute='get_solicitante')
    fecha_solicitud=fields.Date("Fecha Solicitud")
    destino=fields.Char("Destino")
    mision_oficial=fields.Char("Mision Oficial",track_visibilty='always')
    programada=fields.Selection(selection=[('Programada', 'Programada')
                                        ,('No Programada', 'No Programada')]
                                        , string='Tipo de solicitud')
    fecha_salida=fields.Datetime("Fecha Salida")
    fecha_salida_real=fields.Datetime("Fecha y hora de Salida Real")
    fecha_regreso_esperada=fields.Datetime("Fecha Regreso estimado")
    fecha_regreso=fields.Datetime("Fecha Regreso")
    asistieron_ids=fields.Many2many(comodel_name='hr.employee', string='Asistieron')
    encargado_revision_id=fields.Many2one(comodel_name='res.users', string='Encargado de revision')
    encargado_autorizacion_id=fields.Many2one(comodel_name='res.users', string='Encargado de autorizacion')
    conductor_id=fields.Many2one(comodel_name='hr.employee', string='Conductor')
    odometros_ids=fields.One2many('fleet.vehicle.odometer','solicitud_id', 'Marcaciones')
    state=fields.Selection(selection=[('Borrador', 'Borrador')
                                        ,('Solicitado', 'Solicitado')
                                        ,('Autorizado', 'Autorizado')
                                        ,('Asignado', 'Asignado')
                                        ,('En curso', 'En curso')
                                        ,('Finalizado', 'Finalizado')
                                        ,('Cancelado', 'Cancelado')]
                                        , string='Estado',default='Borrador',track_visibilty='always')
    def solicitar(self):
        for record in self:
            record.state='Solicitado'
        template = self.env.ref('fiaes.SolicitudVehiculo', False)
        self.env['mail.template'].browse(template.id).send_mail(self[0])

    def autorizar(self):
        for record in self:
            record.state='Autorizado'
            record.encargado_revision_id=self.env.user.id

    def asignar(self):
        for record in self:
            record.state='Asignado'
            record.encargado_revision_id=self.env.user.id
            if not record.vehicle_id:
                raise ValidationError("Debe especificar el vehiculo asignado")

    def iniciar(self):
        for record in self:
            record.state='En curso'

    def finalizar(self):
        for record in self:
            record.state='Finalizado'

    def cancelar(self):
        for record in self:
            record.state='Cancelado'

    @api.one
    @api.depends('vehicle_id')
    def get_vehicle(self):
        for record in self:
            if record.vehicle_id:
                vehicle_name=record.vehicle_id.model.name + record.vehicle_id.license_plate

    @api.one
    @api.depends('solicitante_tipo','solicitante_employee_id','solicitante_partner_id')
    def get_solicitante(self):
        for record in self:
            if record.solicitante_tipo=='Empleado':
                if record.solicitante_employee_id:
                    record.solicitante=record.solicitante_employee_id.name
                    record.source_email=record.solicitante_employee_id.work_email
            else:
                if record.solicitante_partner_id:
                    record.solicitante=record.solicitante_partner_id.name
                    record.source_email=record.solicitante_partner_id.email



class usovehiculo_detalle(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    odometro_regreso=fields.Integer("Kilometraje de regreso")
    odometro_salida=fields.Integer("Kilometraje de salida")
    fecha_salida=fields.Datetime("Fecha Salida")
    fecha_regreso=fields.Datetime("Fecha Regreso")
    comentario=fields.Char("Comentario")
    solicitud_id=fields.Many2one(comodel_name='fiaes.solicitud_vehiculo', string='Solicitud')
    solicitante=fields.Char(string='Solicitante',compute='get_solicitante',related='solicitud_id.solicitante')
    destino=fields.Char("Destino",related='solicitud_id.destino')
    mision_oficial=fields.Char("Mision Oficial",track_visibilty='always',related='solicitud_id.mision_oficial')
    conductor_id=fields.Many2one(comodel_name='hr.employee', string='Conductor',related='solicitud_id.conductor_id')
    programada=fields.Selection(selection=[('Programada', 'Programada')
                                        ,('No Programada', 'No Programada')]
                                        , string='Tipo de solicitud',related='solicitud_id.programada')


class vehiculo_clase(models.Model):
    _name='fiaes.vehiculo_clase'
    _description='Clase de vehiculo'
    name=fields.Char("Clase de vehiculo")

class vehiculo_tipo(models.Model):
    _name='fiaes.vehiculo_tipo'
    _description='Tipos de vehiculo'
    name=fields.Char("Tipo de vehiculo")


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
    salida_gas=fields.Selection(selection=[('0.25', '1/4')
                                        ,('0.5', '1/2')
                                        ,('0.75', '3/4')
                                        ,('1', 'Full')]
                                        , string='Combustible de salida')
    retorno_fecha=fields.Date("Fecha retorno")
    retorno_km=fields.Integer("Kilometraje de retorno")
    retorno_gas=fields.Selection(selection=[('0.25', '1/4')
                                        ,('0.5', '1/2')
                                        ,('0.75', '3/4')
                                        ,('1', 'Full')]
                                        , string='Combustible de regreso')
    diagnostico=fields.Text("Diagnostico")
    purchase_order_id=fields.Many2one(comodel_name='purchase.order', string='Orden de compra')
    apecto_ids=fields.Many2many(comodel_name='fiaes.vehiculo_aspecto', string='Aspectos a revisar')
    salida_encargado_id=fields.Many2one(comodel_name='hr.employee', string='Encargado de salida')
    retorno_encargado_id=fields.Many2one(comodel_name='hr.employee', string='Encargado de recepcion')


class activo_property(models.Model):
    _name='fiaes.activo_property'
    _description='Aspecto a Revisar'
    name=fields.Char("Atributo")
    valor=fields.Char("Valor")
    activo_id=fields.Many2one(comodel_name='account.asset.asset', string='Activo')


class activo_property(models.Model):
    _inherit='account.asset.category'
    codigo=fields.Char("Codigo")

class activofijo(models.Model):
    _inherit='account.asset.asset'
    responsable_id=fields.Many2one(comodel_name='hr.employee', string='Responsable')
    ubicacion_id=fields.Many2one(comodel_name='stock.location', string='Ubicacion')
    propiedad_ids=fields.One2many('fiaes.activo_property','activo_id', 'Propiedades')
    marca=fields.Char("Marca")
    modelo=fields.Char("Modelo")
    parent_id=fields.Many2one(comodel_name='account.asset.asset', string='Activo Padre')
    child_ids=fields.One2many('account.asset.asset', 'parent_id' , 'Activo Padre')
    capitalizable=fields.Selection(selection=[('Capitalizable', 'Capitalizable')
                                        ,('No Capitalizable', 'No Capitalizable')]
                                        , string='Tipo de Activo',default='Capitalizable')


    def set_codigo(self):
        for record in self:
            if not record.code:
                codigo='FIAES'
                if record.capitalizable=='Capitalizable':
                    codigo=codigo+'-1'
                    codigo=codigo+'-'+record.category_id.codigo
                    codigo=codigo+'-'+self.env['ir.sequence'].next_by_code('fiaes.activo.capitalizable')
                else:
                    codigo=codigo+'-0'
                    codigo=codigo+'-'+record.category_id.codigo
                    codigo=codigo+'-'+self.env['ir.sequence'].next_by_code('fiaes.activo.nocapitalizable')
                record.write({'code':codigo})

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



class red(models.Model):
    _name='fiaes.red'
    _description='Redes'
    tipo=fields.Selection(selection=[('Contacto', 'Contacto')
                                        ,('Otro', 'Otro')]
                                        , string='Tipo',default='Contacto')
    otro=fields.Char("Nombre")
    name=fields.Char(string='Nombre',compute='get_nombre')
    partner_id=fields.Many2one(comodel_name='res.partner', string='Contacto')
    abreviatura=fields.Char("Abreviatura")
    alcance=fields.Selection(selection=[('Nacional', 'Nacional')
                                        ,('Regional', 'Regional')
                                        ,('Mundial', 'Mundial')]
                                        , string='Alcance',default='Nacional')
    puntofocal=fields.Char("Punto focal")
    contacto=fields.Char("Nombre del contacto del punto focal")
    correo=fields.Char("Correo electronico")
    telefono=fields.Char("Telefono")
    direccion=fields.Char("Direccion")
    miembros=fields.Many2many(comodel_name='res.partner', string='Miembros')
    sede=fields.Many2one(comodel_name='res.country', string='Sede')
    estado=fields.Selection(selection=[('Acreditado', 'Acreditado')
                                        ,('No Acreditado', 'No Acreditado')
                                        ,('En proceso', 'En proceso de agreditacion')]
                                        , string='Estado',default='No Acreditado')
    @api.one
    @api.depends('tipo','otro','partner_id')
    def get_nombre(self):
        for record in self:
            if record.tipo=='Contacto':
                if record.partner_id:
                    record.name=record.partner_id.name
            else:
                if record.otro:
                    record.name=record.otro


#Proyecto institucional
class proyecto_institucional(models.Model):
    _inherit='project.project'
    codigo=fields.Char("Codigo")
    tipo=fields.Selection(selection=[('Institucional', 'Proyecto Institucional')
                                        ,('Administrado', 'Administrado')]
                                        , string='Tipo de Proyecto',default='Institucional')
    fuente_ids=fields.Many2many(comodel_name='fiaes.fuente', relation='proyecto_fuente_rel',string='Fuentes')
    contacto_ids=fields.Many2many(comodel_name='res.partner', relation='proyecto_contacto_rel', string='Contactos')
    responsable_ids=fields.Many2many(comodel_name='res.partner', relation='proyecto_responsable_rel', string='Responsable')
    cordenada_ids=fields.One2many('fiaes.proyecto_cordenadas','proyecto_id', 'Cordenadas')
    objetivo_ids=fields.One2many('fiaes.proyecto_objetivo','proyecto_id', 'Objetivos especificos')
    territorio_id=fields.Many2one(comodel_name='fiaes.territorio', string='Territorio')
    objetivo=fields.Text("Objetivo General")


class proyecto_objetivo(models.Model):
    _name = "fiaes.proyecto_objetivo"
    _description = "Objetivos especificos"
    name = fields.Char('Obetivo')
    proyecto_id=fields.Many2one(comodel_name='project.project', string='Proyecto')




class proyecto_cordenadas(models.Model):
    _name = "fiaes.proyecto_cordenadas"
    _description = "Cordenadas donde se desarrolla el proyecto"
    name = fields.Char('Descripcion')
    coordenadas_latitud=fields.Float("Latitud",digits=(20,7))
    coordenadas_longitud=fields.Float("Longitud",digits=(20,7))
    proyecto_id=fields.Many2one(comodel_name='project.project', string='Proyecto')

class task_institucional(models.Model):
    _inherit='project.task'
    codigo=fields.Char("Codigo")
    objetivo_id=fields.Many2one(comodel_name='fiaes.proyecto_objetivo', string='Objetivo')
    tipo=fields.Selection(selection=[('Institucional', 'Proyecto Institucional')
                                        ,('Administrado', 'Administrado')]
                                        , string='Tipo de Proyecto',related="project_id.tipo")
    responsable_ids=fields.Many2many(comodel_name='res.partner', relation='task_responsable_rel', string='Responsables')
    cordinacion_ids=fields.Many2many(comodel_name='res.partner', relation='task_cordinacion_rel', string='En coordinacion')
    inicio=fields.Date("Fecha de inicio")
    fin=fields.Date("Fecha de fin")
    cordenada_ids=fields.One2many('fiaes.task_cordenadas','task_id', 'Cordenadas')
    recurso_ids=fields.One2many('fiaes.task_recurso','task_id', 'Recursos')

class task_cordenadas(models.Model):
    _name = "fiaes.task_cordenadas"
    _description = "Cordenadas donde se desarrolla el proyecto"
    name = fields.Char('Descripcion')
    coordenadas_latitud=fields.Float("Latitud",digits=(20,7))
    coordenadas_longitud=fields.Float("Longitud",digits=(20,7))
    task_id=fields.Many2one(comodel_name='project.task', string='Actividad')

class task_recursos(models.Model):
    _name = "fiaes.task_recurso"
    _description = "Recursos institucionales"
    name = fields.Char('Nombre')
    cantidad=fields.Float("Cantidad",digits=(20,3))
    descripcion = fields.Char('Descripcion')
    account_id=fields.Many2one(comodel_name='account.account', string='Cuenta asociada')
    valor=fields.Float("Valor estimado",digits=(20,3))
    task_id=fields.Many2one(comodel_name='project.task', string='Actividad')
    tipo=fields.Selection(selection=[('Institucional', 'Proyecto Institucional')
                                        ,('Administrado', 'Administrado')]
                                        , string='Tipo de Proyecto',related="task_id.tipo")


class unidad(models.Model):
    _inherit='hr.department'
    codigo=fields.Char("Codigo")
