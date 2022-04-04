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


class odoosv_empleado(models.Model):
    _inherit='hr.employee'
    #Datos generales
    nombre=fields.Char("Nombre")
    apellido=fields.Char("Primer Apellido")
    apellido2=fields.Char("Segundo Apellido")
    apellido_casada=fields.Char("Apellido de casada")
    dui=fields.Char("DUI")
    dui_lugar=fields.Char("Lugar de expedición del DUI")
    dui_fecha=fields.Date("Fecha de expedición del DUI")
    nit=fields.Char("NIT")
    profesion=fields.Char("Profesion/Officio")
    pasaporte=fields.Char("Pasaporte")
    nup=fields.Char("NUP")
    isss=fields.Char("ISSS")
    afp=fields.Char("Nombre de la AFP")
    direccion=fields.Char("Direccion")
    domicilio=fields.Char("Domicilio")
    edad=fields.Char("Edad",compute='_get_edad')
    beneficiario_ids=fields.One2many(comodel_name='odoosv.empleado_beneficiario',inverse_name='empleado_id',string='Beneficiarios')
    prestamo_ids=fields.One2many(comodel_name='odoosv.empleado_prestamo',inverse_name='empleado_id',string='Prestamos')
    cuenta=fields.Char("Cuenta Bancaria")
    codigo=fields.Char("Codigo")

    #Datos de empleo
    fecha_inicio=fields.Char("Fecha de inicio")
    fecha_retiro=fields.Char("Fecha de Retiro")
    

    @api.depends('birthday')
    def _get_edad(self):
        for r in self:
            edad=0
            if self.birthday:
                edad = (datetime.now().date() - self.birthday).days / 365.2425
                edad = int(edad)
                if int(edad) < 0:
                    edad=0
            r.edad=edad

class odoosv_contract(models.Model):
    _inherit='hr.contract'
    aplica_horas_extra=fields.Boolean("Aplicar horas extra")




class odoosv_beneficiario(models.Model):
    _name='odoosv.empleado_beneficiario'
    _description='Benficiarios de los empleados'
    name=fields.Char("Nombre")
    parentezco=fields.Char("Parentezco")
    fecha_nacimiento=fields.Date("Fecha de nacimiento")
    porcentaje=fields.Float("Porcentaje")
    empleado_id=fields.Many2one(comodel_name='hr.employee',string='Empleado')

    @api.constrains('porcentaje')
    def _check_restriciones(self):
        for l in self:
            if l.porcentaje<0:
                raise ValidationError('El porcentaje debe ser mayor que 0')


class odoosv_prestamo(models.Model):
    _name='odoosv.empleado_prestamo'
    _description='Prestamos de empleados'
    name=fields.Char("Referencia")
    financiera_id=fields.Many2one(comodel_name='odoosv.hr_financiera',string='Institucion')
    empleado_id=fields.Many2one(comodel_name='hr.employee',string='Empleado')
    monto=fields.Float("Monto")
    fecha_inicio=fields.Date("Fecha de inicio")
    fecha_fin=fields.Date("Fecha de última cuota")
    cuota_quincena1=fields.Float("Cuota primera Quincena")
    cuota_quincena2=fields.Float("Cuota segunda Quincena")



class odoosv_institucio(models.Model):
    _name='odoosv.hr_financiera'
    _description='Institucion financiera'
    name=fields.Char('Nombre de la institucion')
    codigo=fields.Char('Código para cálculos')
    estructura_id=fields.Many2one(comodel_name='hr.payroll.structure',string='Structura Salarial para genera regla')


    def crear_regla(self):
        for r in self:
            dic={}
            dic['name']=r.name
            dic['code']='r_'+r.codigo
            dic['active']=True
            dic['sequence']=260
            dic['appears_on_payslip']=True
            dic['condition_select']='python'
            dic['condition_python']="""
monto=0.0
for p in employee.prestamo_ids:
    if p.financiera_id.codigo=='"""+r.codigo+"""':
        if p.fecha_inicio<payslip.date_from:
            if p.fecha_fin>payslip.date_from:
                if payslip.payslip_run_id.quincena=='1':
                    monto=p.cuota_quincena1
                if payslip.payslip_run_id.quincena=='2':
                    monto=p.cuota_quincena2
result = (monto>0)
            """
            dic['amount_select']='code'
            dic['category_id']=self.env.ref('sv_rrhh.sv_panilla_group_banco').id
            dic['struct_id']=r.estructura_id.id
            dic['amount_python_compute']="""
monto=0.0
for p in employee.prestamo_ids:
    if p.financiera_id.codigo=='"""+r.codigo+"""':
        if p.fecha_inicio<payslip.date_from:
            if p.fecha_fin>payslip.date_from:
                if payslip.payslip_run_id.quincena=='1':
                    monto=p.cuota_quincena1
                if payslip.payslip_run_id.quincena=='2':
                    monto=p.cuota_quincena2
result = round(monto*-1,2)
            """
            self.env['hr.salary.rule'].create(dic)



class odoosv_payslip(models.Model):
    _inherit='hr.payslip'
    horas_extra=fields.Float('Horas Extra')
    horas_extra_nocturna=fields.Float('Horas Extra Nocturnas')
    horas_asueto=fields.Float('Horas Asueto')
    dias_vacaciones=fields.Float('Dias de vacaciones')
    dias_incapacidad=fields.Float('Dias de incapacidad')
    otros_ingresos=fields.Float('Otros ingresos')
    otros_descuentos=fields.Float('Otros descuentos')

class odoosv_paysliprun(models.Model):
    _inherit='hr.payslip.run'
    estructura_id=fields.Many2one(comodel_name='hr.payroll.structure',string='Structura Salarial')
    fecha_calculo=fields.Date("Fecha de calculo")
    fecha_considerar=fields.Date("Fecha a considerar")
    comentario=fields.Text("Comentario")
    quincena=fields.Selection(selection=[('1', 'Quincena 1')
                                    ,('2', 'Quincena 2')
                                    ,('3', 'Otra')]
                                    , string='Quincena',default='1')
    reporte_planilla=fields.Char("Reporte Planilla",compute='compute_reportes')
    reporte_planilla_patronal=fields.Char("Reporte Planilla Patronal",compute='compute_reportes')
    reporte_recibos=fields.Char("Reporte Recibos",compute='compute_reportes')

    def calcular(self):
        for r in self:
            for p in r.slip_ids:
                p.write({'struct_id':r.estructura_id})
                p.compute_sheet()

    def imprimir(self):
        x=1

    def compute_reportes(self):
        for r in self:
            texto1=''
            texto2=''
            texto3=''
            jasper=r.company_id.jasper
            if not jasper:
                jasper=self.env['odoosv.jasper'].search([('name','=','odoo')],limit=1)
            if jasper:
                texto1=jasper.create_link_report('/sv/reportes/hr','Planilla',r.id,'')
                texto2=jasper.create_link_report('/sv/reportes/hr','PlanillaPatronal',r.id,'')
                texto3=jasper.create_link_report('/sv/reportes/hr','Recibos',r.id,'')
            r.reporte_planilla=texto1
            r.reporte_planilla_patronal=texto2
            r.reporte_recibos=texto3

#############
class jasper_account_move(models.Model):
    _inherit='account.move'
   
    
    def compute_fiscalreport(self):
        for r in self:
            texto=''
            jasper=r.company_id.jasper
            if not jasper:
                jasper=self.env['odoosv.jasper'].search([('name','=','odoo')],limit=1)
            if jasper:
                if r.tipo_documento_id:
                    if r.tipo_documento_id.formato:
                        texto=jasper.create_link_report('/sv/reportes/transacciones',r.tipo_documento_id.formato,r.id,'pdf')
            r.formato_fiscal=texto


class jasrper_journal(models.Model):
    _inherit='account.journal'
    

    @api.depends('check_next_number','numero_cheque_maximo')
    def _get_disponible(self):
        for r in self:
            resultado=0
            try:
                if r.check_next_number and r.numero_cheque_maximo:
                    a=int(r.check_next_number)
                    b=int(r.numero_cheque_maximo)
                    resultado=b-a
            except:
                print("Hubo un error")
            r.cheques_disponibles=resultado


