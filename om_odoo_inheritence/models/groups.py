from odoo import models, fields, api


class ResGroups(models.Model):
    _inherit = 'res.groups'

    def get_application_groups(self, domain):
        group_id = self.env.ref('sale_management.group_sale_order_template').id
        return super(ResGroups, self).get_application_groups(domain + [('id','!=',(group_id))])