from odoo import models, fields, api


class saleOrder(models.Model):
    _inherit = 'sale.order'


    confirmed_user_id = fields.Many2one('res.users', string='Confirmed Users')


    def action_confirm(self):
        super(saleOrder, self).action_confirm
        self.confirmed_user_id = self.env.user.id

    def _prepare_invoice_values(self):
        invoic_vals = super(saleOrder, self)._prepare_invoice_values()
        invoic_vals['so_confirmed_user_id'] = self.confirmed_user_id.id
        return invoic_vals
