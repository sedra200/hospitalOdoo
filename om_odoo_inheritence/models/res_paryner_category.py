from odoo import fields, models, api


class ParnterCategory(models.Model):
    _name = 'res.partner.category'
    _inherit = ['res.partner.category', 'mail.thread']

    name = fields.Char(tracking=True)




