# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    facturae_auto_dates = fields.Boolean("Auto Dates")
