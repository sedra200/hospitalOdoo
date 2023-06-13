from odoo import api, fields, models
import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date

class CancelAppointmentWizard(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CancelAppointmentWizard, self).default_get(fields)
        res['date_cancel'] =  datetime.date.today()
        return res

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment", domain=['|',('state', '=', 'draft'),('priority', 'in', ('0',False))])
    reson = fields.Text(string="Reson")
    date_cancel = fields.Date(string="Cancelation Date")

    def action_cancel(self):
        cancel_day = int(self.env['ir.config_parameter'].get_param('om.cancel_day'))
        allowed_date = self.appointment_id.booking_date - relativedelta(days=cancel_day)
        chosen_date = fields.Date.from_string(self.date_cancel)
        print(cancel_day)
        print(allowed_date)
        print(chosen_date)

        if chosen_date > allowed_date:
            raise ValidationError("Sorry, cancellation is not allowed for this booking")

        self.appointment_id.state = 'cancel'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cancel.appointment.wizard',
            'target': 'new',
        }








