# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PMSTinyReservation(models.Model):
    _inherit = "pms.tiny.reservation"

    anphitrion_bind_ids = fields.One2many(
        comodel_name="anphitrion.pms.tiny.reservation",
        inverse_name="odoo_id",
        string="Anphitrion Bindings",
    )
