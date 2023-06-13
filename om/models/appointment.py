from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Hospitalappointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital appointment"
    # rec_name for show name of the patient in the top after Hospital/patient_name
    _rec_name = 'patient_id'
    _order = 'id desc'

    name = fields.Char(string='Sequence', default='New', tracking=True)
    # ondelete = restrict means if a record is refrenced by other record will raise an error and it use inlt with M2O or O2M
    patient_id = fields.Many2one('hospital.patient', string="Patient", ondelete='restrict', tracking=1)
    appointment_time = fields.Datetime(string='Appointment Time', default=fields.Datetime.now)
    # related = allows to access and display the value from related model without creating a direct database relation
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], related='patient_id.gender')
    booking_date = fields.Date(string='Booking Date', default=fields.Date.context_today,
                               help="Write the date of pateint appointment", tracking=True)
    ref = fields.Char(string='Refrence')
    prescription = fields.Html(string='Prescription')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),

    ], string="Priority")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_conslution', 'In_Conslution'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], default='draft', string='Status', required=True)
    doctor_id = fields.Many2one('res.users', string="Doctor", tracking=2)
    pharmacy_line_ids = fields.One2many('appointment.pharmacy', 'appointment_id', string='Pharmacy Line', tracking=True)
    hide_sales_price = fields.Boolean(string="Hide sales price")
    operation = fields.Many2one('hospital.operation', string="Operation")
    progress = fields.Integer(string='Progress', compute='_compute_progress')
    duration = fields.Float(string="Duration", tracking=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
        res = super(Hospitalappointment, self).create(vals)
        sl_no = 0
        for line in res.pharmacy_line_ids:
            sl_no += 1
            line.sl_no = sl_no
        return res

    def write(self, values):
        res = super(Hospitalappointment, self).write(values)
        sl_no = 0
        for line in self.pharmacy_line_ids:
            sl_no += 1
            line.sl_no = sl_no

    def unlike(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("you cannot delete this recorde because is not draft record")
            return super(Hospitalappointment, self).unlike()

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    # the function below is for show message when we click on button with the object action_test
    # and we can put self.fiels_name instead the www...
    def action_test(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': 'https://www.odooo.com'
        }

    def action_in_consulation(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'in_conslution'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
        return {
            'effect': {
                'fedeout': 'slow',
                'message': 'Click successfuly',
                'type': 'rainbow_man',
            }
        }

    def action_in_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                progress = 25
            elif rec.state == 'in_conslution':
                progress = 50
            elif rec.state == 'done':
                progress = 100
            else:
                progress = 0
            rec.progress = progress

    def action_share_whatsapp(self):
        # this %s will change with the value after %
        if not self.patient_id.phone:
            raise ValidationError("Missing number for this patient!")
        msg = 'Hello *%s*, your *appointment* number is: %s , Thank You!' % (self.patient_id.name, self.name)
        whatapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.phone, msg)
        self.message_post(body=msg, subject='Whatsapp Message')
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatapp_api_url
        }

    def action_notification(self):
        action = self.env.ref('om.action_hospital_patient')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Click to open patient recird'),
                'message': '%s',
                'links': [{
                    'label': self.patient_id.name,
                    'url': f'#action={action.id}&id={self.patient_id.id}&model=hospital.patient',
                }],
                'sticky': False,

            }

        }

    def action_send_mail(self):
        template = self.env.ref('om.appointment_main_template')
        print("aaaaaaaaa")
        for rec in self:
            template.send_mail(rec.id, force_send=True)


class AppointmentPharmcyLine(models.Model):
    _name = "appointment.pharmacy"
    _description = "Appointment Pharmacy"

    sl_no = fields.Integer(string="SNO.")
    product_id = fields.Many2one('product.product')
    price_unite = fields.Float(string="Price")
    qty = fields.Integer(string="Quantity")
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
    # currency_field This attribute indicates that the currency used for the monetary field will be determined by the field company_currency_id.

    price_subtotal = fields.Monetary(string="Subtotal", compute="_compute_price_subtotal",
                                     currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency', related='appointment_id.currency_id')

    @api.depends('price_unite', 'qty')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unite * rec.qty
