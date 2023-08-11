# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models


class PMSTinyAstrochannelServiceGuest(models.Model):
    _name = "pms.tiny.astrochannel.service.guest"
    _description = "Astrochannel Service Guest Mappings"

    service_id = fields.Many2one(
        string="Astrochannel Service",
        comodel_name="pms.tiny.astrochannel.service",
        required=True,
        ondelete="cascade",
    )

    tipofac = fields.Char(string="TipoFac", required=True)
    guest_type = fields.Selection(
        selection=[("adult", _("Adult")), ("child", _("Child")), ("baby", _("Baby"))],
        required=True,
    )

    _sql_constraints = [
        (
            "uniq",
            "unique(service_id, tipofac)",
            "A TipoFac is already mapped",
        ),
    ]
