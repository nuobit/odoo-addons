# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models


class PMSTinyAPIAstroportalGuest(models.Model):
    _name = "pms.tiny.api.astroportal.guest"
    _description = "Astroportales API guest mappings"

    api_astroportal_id = fields.Many2one(
        string="Astroportal API",
        comodel_name="pms.tiny.api.astroportal",
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
            "agb_tipofac_uniq",
            "unique(api_astroportal_id, tipofac)",
            "A TipoFac is already mapped",
        ),
    ]
