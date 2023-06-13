from odoo import api, fields, models, _
import datetime
from datetime import date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    # mail.thread = by inherited this model the new model will have access features sush as sendeing and receiving tracking message
    # mail.activity.mixin = It allows tracking of different activities related to the model, such as logging notes, creating tasks, and setting reminders.
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Patient"

    name = fields.Char(string='Name', tracking=True)
    date_of_brith = fields.Date(string='Data of Birth')
    ref = fields.Char(string='Refrence')
    # compute used to calculate values dynamically
    # inverse is used to be able too update the field if it was fro the type compute
    age = fields.Integer(string='Age', compute='_compute_age', inverse='_inverse_compute_age', search='_search_age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    active = fields.Boolean(string="Active", default=True)
    image = fields.Image(string="Image")
    tags_ids = fields.Many2many('patient.tag', string="Tags")
    appointment_count = fields.Integer(string="Appointment Count", compute='_compute_appointment_count', store=True)
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string="Appointment Id")
    parent = fields.Char(string="Parent")
    marital_status = fields.Selection([('married', 'Marrid'), ('single', 'Single')], string="Marital Status")
    partner_name = fields.Char(string="Partner Name")
    is_birthday = fields.Boolean(string="Is Birthday!", compute='_compute_is_birthday')
    phone = fields.Char(string="Phone Number")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")

    # to create a value auto for spesific field, vals wil store all info inside the form and when we give it a value will fill the fiels we chose it without enter anything
    # used to create new record
    @api.model
    def create(self, vals):
        vals['ref'] = 'Ompt'
        return super(HospitalPatient, self).create(vals)

    # search_count count the number of records that match a specific search
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for patient in self:
            appointment_count = 0
            for appointment in patient.appointment_ids:
                appointment_count += 1
            patient.appointment_count = appointment_count

    # The code is checking if the date of birth is greater than today's date.
    @api.constrains('date_of_brith')
    def _check_date_of_brith(self):
        for record in self:
            if record.date_of_brith > fields.Date.to_date(datetime.datetime.today()):
                raise ValidationError("The entered date of birth is invalid!")

    # the function below will add to ref value if we didn't write it
    # used to update an existing record in modul
    def write(self, val):
        print("it's work for writting")
        if not self.ref:
            val['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).write(val)

    @api.depends('date_of_brith')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_brith:
                rec.age = today.year - rec.date_of_brith.year
            else:
                rec.age = 1

    # the function bellow will delete based on condition in this case the function will not delete if r=the patient has an appointment
    @api.ondelete(at_uninstall=False)
    def _check_appointemnt(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError("You cannot delete that record because it has an appointment")

    # when we have many patient in the same name and we want to put another sign next to the name we use the function bellow
    # this function will show the ref next to the name
    # @api.model
    # def name_get(self):
    # patient_list = []
    # for record in self:
    # name = str(record.ref) + " " + record.name
    # patient_list.append((record.id, name))
    # return patient_list

    @api.onchange('age')
    def _onchange_age(self):
        today = date.today()
        for rec in self:
            rec.date_of_brith = today - relativedelta(years=rec.age)

    @api.onchange('age')
    def _inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.date_of_brith = today - relativedelta(years=rec.age)

    def _search_age(self, operator, value):
        print(value)
        return [('id', '=', 13)]

    @api.depends('date_of_brith')
    def _compute_is_birthday(self):
        for rec in self:
            is_birthday = False
            if rec.date_of_brith:
                today = date.today()
                if today.day == rec.date_of_brith.day and today.month == rec.date_of_brith.month:
                    is_birthday = True
            rec.is_birthday = is_birthday

    # this function for the smart button which will take us to the appointment page that related to the same patient
    def action_view_appointment(self):
        return {
            'name': _('Appointment'),
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form,calendar',
            'context': {},
            'domain': [('patient_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }
