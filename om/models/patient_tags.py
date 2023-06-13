from odoo import api, fields, models


class PatientTags(models.Model):
    _name = "patient.tag"
    _description = "Patient Tag"

    name = fields.Char(string="Name", required=True, trim=False)
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color")
    color_2 = fields.Char(string="Color_2")
    sequence = fields.Integer(string="Sequence")

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = self.name + "(Copy)"
        default['sequence'] = 10
        return super(PatientTags, self).copy(default)

    _sql_constraints = [
        ('unique_tag_name', 'unique (name, active)', 'Name must be unique'),
        ('check_sequence', 'check (sequence > 0)', 'Sequence must be greater than five')
    ]
