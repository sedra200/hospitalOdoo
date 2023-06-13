from odoo import api, fields, models


class HospitalOperation(models.Model):
    _name = "hospital.operation"
    _description = "Hospital Operation"
    _log_access = False
    _order = "sequence,id"

    doctor_id = fields.Many2one('res.users', string="Doctor")
    operation_name = fields.Char('Name')
    reference_record = fields.Reference(selection=[('hospital.patient', 'patient'),
                                                   ('hospital.appointment', 'Appointment')], string="Record")
    sequence = fields.Integer(string="Sequence", defailt=10)

    # The @api.model decorator is used to indicate that the method is a static method and does not require access to the current record or the environment.

    @api.model
    def name_create(self, name):
        return self.create({'operation_name': name}).name.get()[0]
