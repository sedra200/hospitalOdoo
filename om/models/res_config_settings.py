# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    # This attribute sets a configuration parameter for the field. A configuration parameter allows you to
    # set a value that can be configured and changed without modifying the code
    cancel_days = fields.Integer(string='Cancel Days', config_parameter='om.cancel_day')
