# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IrChecksum(models.Model):
    _inherit = "ir.checksum"

    wordpress_bind_ids = fields.One2many(
        comodel_name="wordpress.ir.checksum",
        inverse_name="odoo_id",
        string="WordPress Bindings",
    )
    wordpress_write_date = fields.Datetime(
        compute="_compute_wordpress_write_date",
        store=True,
    )

    @api.depends("title", "alternate_text", "store_fname", "mimetype", "checksum")
    def _compute_wordpress_write_date(self):
        for rec in self:
            rec.wordpress_write_date = fields.Datetime.now()

    _sql_constraints = [
        (
            "external_uniq",
            "unique(checksum)",
            "A checksum already exists with the same External (checksum) ID.",
        ),
    ]

    def write(self, vals):
        if "checksum" in vals:
            raise ValidationError(
                _("You cannot change the checksum of an existing record.")
            )
        return super().write(vals)
